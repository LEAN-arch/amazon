import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please return to the 'Global Command Center' home page to initialize the app.")
    st.stop()

# --- UI RENDER ---
st.markdown("# ⚖️ NPI & Strategic Sourcing Hub")
st.markdown("This hub provides a data-driven framework for selecting and qualifying suppliers capable of delivering **aerospace quality at unprecedented scale** for the Kuiper mission.")

# --- DATA DEFINITION & INPUT ---
@st.cache_data
def get_sourcing_data():
    # This dictionary represents the raw, objective data collected for each potential supplier.
    # Metrics have been expanded to be highly relevant to the Kuiper project.
    sourcing_data = {
        'Supplier': ['Future Foundries LLC', 'Global Test Solutions', 'NextGen Packaging', 'AeroChip Test'],
        # --- Quality System Maturity ---
        'AS9100D Certified (1=Yes, 0=No)': [1, 1, 0, 1],
        'Export Control Compliant (1=Yes, 0=No)': [1, 1, 1, 1], # Crucial for Kuiper
        'Avg SCAR Closure (Days)': [25, 18, 45, 15],
        # --- Technical & Process Capability ---
        'Rad-Hard Process Maturity (1-5)': [4, 3, 2, 5], # Kuiper-specific
        'Avg Cpk (Critical Params)': [1.45, 1.35, 1.10, 1.67],
        'First Pass Yield (%)': [99.1, 99.5, 97.0, 99.8],
        # --- Cost & Commercial ---
        'Quoted Unit Cost ($)': [2.50, 1.80, 1.50, 2.75],
        'Est. COPQ (% of Spend)': [1.0, 1.5, 5.0, 0.5],
        # --- Scalability & Supply Chain ---
        'Volume Ramp Readiness (1-5)': [3, 4, 2, 5], # Kuiper-specific
        'Capacity Utilization (%)': [70, 85, 95, 65],
        'BCP Audit Score (1-5)': [4, 3, 2, 5],
    }
    return pd.DataFrame(sourcing_data)

# --- SCORING LOGIC ---
def calculate_scores(df):
    scored_df = df[['Supplier']].copy()
    scored_df['QMS_Score'] = ((df['AS9100D Certified (1=Yes, 0=No)'] * 40) + (df['Export Control Compliant (1=Yes, 0=No)'] * 40) + ((1 - (df['Avg SCAR Closure (Days)'] / 60)) * 20))
    scored_df['Tech_Score'] = (((df['Rad-Hard Process Maturity (1-5)'] / 5) * 40) + (np.clip((df['Avg Cpk (Critical Params)'] - 1.0) / 0.67, 0, 1) * 40) + (np.clip((df['First Pass Yield (%)'] - 97) / 2.8, 0, 1) * 20))
    scored_df['Cost_Score'] = ((df['Quoted Unit Cost ($)'].min() / df['Quoted Unit Cost ($)']) * 60 + ((1 - (df['Est. COPQ (% of Spend)'] / 10)) * 40))
    scored_df['Scale_Score'] = (((df['Volume Ramp Readiness (1-5)'] / 5) * 40) + ((1 - (df['Capacity Utilization (%)'] / 100)) * 30) + ((df['BCP Audit Score (1-5)'] / 5) * 30))
    return scored_df.round(1)

# --- TABS FOR WORKFLOW ---
tab_decision, tab_audit = st.tabs(["📊 Supplier Decision Matrix", "📝 Qualification Audit Deep Dive"])

with tab_decision:
    st.header("Multi-Criteria Decision Matrix (MCDM) for Supplier Selection")
    st.markdown("- **Why (Actionability):** This demonstrates the ability to **\"define requirements and deploy processes\"** for sourcing. It moves beyond a simple cost vs. quality trade-off to a holistic, risk-based decision model. A Sr. SQE can adjust the weights based on the specific needs of the component (e.g., for a mission-critical ASIC, 'Technical Capability' might be weighted heaviest), ensuring the best supplier is chosen.")

    with st.sidebar:
        st.header("Sourcing Decision Weights")
        st.caption("Adjust the importance of each category. Weights must sum to 100.")
        w_qms = st.slider("Quality System Maturity (%)", 0, 100, 30, key="w_qms")
        w_tech = st.slider("Technical Capability (%)", 0, 100, 40, key="w_tech")
        w_scale = st.slider("Scalability & Supply Chain (%)", 0, 100, 20, key="w_scale")
        w_cost = st.slider("Cost & Commercial (%)", 0, 100, 10, key="w_cost")
        total_weight = w_qms + w_tech + w_cost + w_scale
        if total_weight != 100:
            st.error(f"Total weight is {total_weight}%. Please adjust sliders to sum to 100."); st.stop()

    input_df = get_sourcing_data()
    scored_df = calculate_scores(input_df)
    
    final_df = scored_df.copy()
    final_df['Weighted_Score'] = ((final_df['QMS_Score'] * w_qms / 100) + (final_df['Tech_Score'] * w_tech / 100) + (final_df['Cost_Score'] * w_cost / 100) + (final_df['Scale_Score'] * w_scale / 100))

    st.subheader("Supplier Scorecard & Recommendation")
    st.dataframe(final_df.sort_values("Weighted_Score", ascending=False), use_container_width=True,
        column_config={
            "QMS_Score": st.column_config.ProgressColumn("QMS Score", min_value=0, max_value=100),
            "Tech_Score": st.column_config.ProgressColumn("Tech Score", min_value=0, max_value=100),
            "Cost_Score": st.column_config.ProgressColumn("Cost Score", min_value=0, max_value=100),
            "Scale_Score": st.column_config.ProgressColumn("Scale Score", min_value=0, max_value=100),
            "Weighted_Score": st.column_config.ProgressColumn("Final Weighted Score", min_value=0, max_value=100, format="%.1f")
        }
    )
    recommended_supplier = final_df.loc[final_df['Weighted_Score'].idxmax()]
    st.success(f"**Recommendation:** Based on the objective data and current weights, **{recommended_supplier['Supplier']}** is the highest-scoring candidate.", icon="🏆")
    
    with st.expander("**SME DEEP DIVE: How Scores Are Calculated (with Standard & Project Relevance)**", expanded=True):
        st.markdown("---")
        st.markdown("#### Quality System Maturity")
        st.markdown("""
        - **`AS9100D Certified`**:
            - **Metric:** A binary check (Yes/No) for certification to the Aerospace Quality Management System standard.
            - **Kuiper Relevance:** This is a **non-negotiable baseline** for any supplier providing mission-critical hardware. It ensures fundamental systems for risk management, configuration control, and traceability are in place.
            - **Standards:** **AS9100D**, **ISO 9001**.
        - **`Export Control Compliant`**:
            - **Metric:** A binary check confirming the supplier's systems are compliant with US export regulations.
            - **Kuiper Relevance:** This is a **legal and program-critical showstopper**. Satellite technology is subject to strict **ITAR/EAR** regulations. A non-compliant supplier in the supply chain creates unacceptable legal and project delay risks.
            - **Standards:** **ITAR (International Traffic in Arms Regulations)**, **EAR (Export Administration Regulations)**.
        - **`Avg SCAR Closure (Days)`**:
            - **Metric:** The average time taken by the supplier to close a formal Supplier Corrective Action Request.
            - **Kuiper Relevance:** Measures responsiveness and problem-solving velocity. In a high-volume program like Kuiper, the ability to resolve issues *quickly* is critical to prevent cascading production line stoppages.
            - **Standards:** Effectiveness of the corrective action process is a key requirement of **AS9100D Clause 10.2**.
        """)
        st.markdown("---")
        st.markdown("#### Technical & Process Capability")
        st.markdown("""
        - **`Rad-Hard Process Maturity`**:
            - **Metric:** A 1-5 rating based on an audit of the supplier's experience and process controls for creating radiation-hardened or radiation-tolerant devices.
            - **Kuiper Relevance:** The most critical technical differentiator. ASICs in Low Earth Orbit (LEO) are constantly bombarded by radiation. A supplier without proven Rad-Hard capability is not viable for critical components.
            - **Standards:** **JEDEC JESD236** (Guideline for Radiation Hardness Assurance), **MIL-STD-883 Test Method 1019**.
        - **`Avg Cpk (Critical Parameters)`**:
            - **Metric:** The average Process Capability Index for key parameters defined on the engineering drawing.
            - **Kuiper Relevance:** Statistical proof of reliability. A high Cpk (>1.33) means the process is tightly controlled and will consistently produce parts well within specification, which is essential for the 5-7 year mission life of a satellite.
            - **Standards:** A core tool of **Six Sigma**, and a key deliverable for process validation under **AS9145 (APQP)** and **IATF 16949**.
        - **`First Pass Yield (%)`**:
            - **Metric:** The percentage of units that pass all tests on their first attempt without any rework.
            - **Kuiper Relevance:** A primary indicator of process stability and efficiency. Low FPY at Kuiper's scale translates to massive scrap costs and introduces quality risks from non-standard rework flows.
            - **Standards:** A Key Performance Indicator (KPI) used to monitor the effectiveness of a QMS under **ISO 9001/AS9100**.
        """)
        st.markdown("---")
        st.markdown("#### Cost & Commercial")
        st.markdown("""
        - **`Quoted Unit Cost ($)`**:
            - **Metric:** The price per ASIC unit.
            - **Kuiper Relevance:** Important for the commercial viability of a large-scale constellation, but must be balanced against quality and reliability.
            - **Standards:** N/A (Commercial Term).
        - **`Est. COPQ (% of Spend)`**:
            - **Metric:** The estimated Cost of Poor Quality, including scrap, rework, and the cost of Amazon's engineering support for supplier issues.
            - **Kuiper Relevance:** This demonstrates a "total cost of ownership" mindset. A supplier with a low unit cost but high COPQ is a false economy and a drain on engineering resources.
            - **Standards:** A foundational concept in **Six Sigma** and Total Quality Management.
        """)
        st.markdown("---")
        st.markdown("#### Scalability & Supply Chain")
        st.markdown("""
        - **`Volume Ramp Readiness`**:
            - **Metric:** A 1-5 rating of the supplier's audited ability to scale from initial production to the high volumes required by Kuiper.
            - **Kuiper Relevance:** This directly addresses the central challenge of the role: "aerospace quality at **unprecedented scale**." A supplier who excels at prototypes but cannot support mass production is not a strategic fit.
            - **Standards:** Relates to **AS9100D Clause 8.1 (Operational Planning)** and formal capacity planning.
        - **`Capacity Utilization (%)`**:
            - **Metric:** The percentage of the supplier's total manufacturing capacity that is already in use.
            - **Kuiper Relevance:** A supplier at 95% utilization is a major risk; they have no buffer for demand upside or to recover from a process excursion. We need partners with available capacity.
            - **Standards:** A key input into the risk assessment for **AS9100D Clause 8.4 (Control of External Providers)**.
        - **`BCP Audit Score`**:
            - **Metric:** A 1-5 rating of the supplier's Business Continuity Plan.
            - **Kuiper Relevance:** Assesses supply chain resilience. What is their plan for a fire, flood, or geopolitical event? For a program with a tight launch cadence, supplier downtime is not an option.
            - **Standards:** Relates to risk-based thinking from **ISO 31000**, which is a foundation for the entire **AS9100D** standard.
        """)

with tab_audit:
    st.header("Qualification Audit Workspace")
    st.markdown("Select a supplier from the NPI pipeline to review their AS9100D qualification audit status and findings.")

    selected_supplier_audit = st.selectbox("Select Supplier for Audit Review", input_df['Supplier'].unique(), key="audit_supplier_select")
    st.info(f"**Viewing Audit Details for:** `{selected_supplier_audit}`")

    audit_progress = np.random.randint(70, 100) if selected_supplier_audit != 'NextGen Packaging' else 45
    audit_status = {
        "7.5 Documented Information": "Passed", "8.1 Operational Planning & Control": "Passed",
        "8.3 Design & Development": "Minor CAR", "8.4 Control of External Providers": "Passed",
        "8.5.1 Control of Production": "Major CAR", "9.1 Monitoring & Measurement": "Passed"
    }
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Audit Progress")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=audit_progress, title={'text': "Overall Audit Completion (%)"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "darkblue"}}))
        st.plotly_chart(fig_gauge, use_container_width=True, key="audit_gauge")
        st.subheader("Key Findings")
        if audit_status["8.5.1 Control of Production"] == "Major CAR": st.error("**Major CAR on 8.5.1:** Lack of documented process for validating special processes (e.g., radiation-hardness assurance). Qualification cannot proceed until resolved.", icon="🚨")
        if audit_status["8.3 Design & Development"] == "Minor CAR": st.warning("**Minor CAR on 8.3:** Inconsistent documentation of design review outputs. Action plan required within 30 days.", icon="⚠️")
        st.success("No other major findings noted.", icon="✅")
    with col2:
        st.subheader("AS9100D Clause Review Status")
        st.markdown("- **Why (Actionability):** This demonstrates the hands-on activity of an **AS9100D Lead Auditor**. It provides a clear, actionable summary of the audit's progress and pinpoints the exact areas of the supplier's Quality Management System that are non-compliant and require corrective action (CARs).")
        for clause, status in audit_status.items():
            if status == "Passed": st.markdown(f"- ✅ **{clause}:** `{status}`")
            elif status == "Minor CAR": st.markdown(f"- ⚠️ **{clause}:** `{status}`")
            else: st.markdown(f"- 🚨 **{clause}:** `{status}`")
