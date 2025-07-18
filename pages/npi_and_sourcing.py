import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np  # <-- THIS WAS THE MISSING IMPORT

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please return to the 'Global Command Center' home page to initialize the app.")
    st.stop()

# --- UI RENDER ---
st.markdown("# 🚀 NPI & Strategic Sourcing Hub")
st.markdown("This hub provides tools for data-driven supplier selection and for managing the rigorous qualification process required for an aerospace supply chain.")

# --- DATA DEFINITION (MOVED OUTSIDE TABS) ---
@st.cache_data
def get_npi_data():
    return pd.DataFrame({
        'Supplier': ['Future Foundries LLC', 'Global Test Solutions', 'NextGen Packaging', 'AeroChip Test'],
        'Part_Type': ['RF ASIC', 'Power Mgmt ASIC', 'Memory Controller', 'Power Mgmt ASIC'],
        'QMS_Score': [85, 92, 78, 95], 'Tech_Score': [90, 85, 88, 98],
        'Cost_Score': [70, 85, 90, 65], 'Scale_Score': [80, 82, 75, 95]
    })
npi_df_base = get_npi_data()

tab_decision, tab_audit = st.tabs(["Supplier Decision Matrix", "Qualification Audit Deep Dive"])

with tab_decision:
    st.header("Multi-Criteria Decision Matrix (MCDM) for Supplier Selection")
    st.markdown("- **Why (Actionability):** This demonstrates the ability to **\"define requirements and deploy processes\"** for sourcing. It moves beyond a simple cost vs. quality trade-off to a holistic, risk-based decision model. A Sr. SQE can adjust the weights based on the specific needs of the component, ensuring the best supplier is chosen.")
    
    with st.sidebar:
        st.header("Sourcing Decision Weights")
        st.caption("Adjust the importance of each category. Weights must sum to 100.")
        w_qms = st.slider("Quality System Maturity (%)", 0, 100, 35, key="w_qms")
        w_tech = st.slider("Technical Capability (%)", 0, 100, 30, key="w_tech")
        w_cost = st.slider("Cost & Commercial (%)", 0, 100, 15, key="w_cost")
        w_scale = st.slider("Scalability & Supply Chain (%)", 0, 100, 20, key="w_scale")
        total_weight = w_qms + w_tech + w_cost + w_scale
        if total_weight != 100:
            st.error(f"Total weight is {total_weight}%. Please adjust sliders to sum to 100."); st.stop()

    npi_df = npi_df_base.copy()
    npi_df['Weighted_Score'] = ((npi_df['QMS_Score'] * w_qms / 100) + (npi_df['Tech_Score'] * w_tech / 100) + (npi_df['Cost_Score'] * w_cost / 100) + (npi_df['Scale_Score'] * w_scale / 100))

    st.subheader("Supplier Scorecard & Recommendation")
    st.dataframe(npi_df.sort_values("Weighted_Score", ascending=False), use_container_width=True, column_config={"Weighted_Score": st.column_config.ProgressColumn("Final Weighted Score", min_value=50, max_value=100, format="%.1f")})
    recommended_supplier = npi_df.loc[npi_df['Weighted_Score'].idxmax()]
    st.success(f"**Recommendation:** Based on the current weights, **{recommended_supplier['Supplier']}** is the highest-scoring candidate.", icon="🏆")
    
    st.subheader("Strategic Sourcing Matrix")
    st.caption("This plot visualizes the final weighted score against the supplier's cost score, providing a final strategic check.")
    fig_scatter = px.scatter(npi_df, x='Cost_Score', y='Weighted_Score', size='Weighted_Score', color='Supplier', hover_name='Supplier', title="Overall Score vs. Cost Score", labels={'Cost_Score': 'Cost Score (Higher is Better)', 'Weighted_Score': 'Final Weighted Score'})
    fig_scatter.add_vline(x=npi_df['Cost_Score'].mean(), line_dash="dash", annotation_text="Avg. Cost Score"); fig_scatter.add_hline(y=npi_df['Weighted_Score'].mean(), line_dash="dash", annotation_text="Avg. Overall Score")
    st.plotly_chart(fig_scatter, use_container_width=True, key="sourcing_scatter_final")

with tab_audit:
    st.header("Qualification Audit Workspace")
    st.markdown("Select a supplier from the NPI pipeline to review their AS9100D qualification audit status and findings.")

    selected_supplier_audit = st.selectbox("Select Supplier for Audit Review", npi_df_base['Supplier'].unique(), key="audit_supplier_select")

    st.info(f"**Viewing Audit Details for:** `{selected_supplier_audit}`")

    # This line will now work correctly
    audit_progress = np.random.randint(70, 100) if selected_supplier_audit != 'NextGen Packaging' else 45
    audit_status = {"7.5 Documented Information": "Passed", "8.1 Operational Planning & Control": "Passed", "8.3 Design & Development": "Minor CAR", "8.4 Control of External Providers": "Passed", "8.5.1 Control of Production": "Major CAR", "9.1 Monitoring & Measurement": "Passed"}
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Audit Progress")
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=audit_progress, title={'text': "Overall Audit Completion (%)"}, gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "darkblue"}}))
        st.plotly_chart(fig_gauge, use_container_width=True, key="audit_gauge")
        st.subheader("Key Findings")
        if audit_status["8.5.1 Control of Production"] == "Major CAR": st.error("**Major CAR on 8.5.1:** Lack of documented process for validating special processes (e.g., wire bonding). Qualification cannot proceed until resolved.", icon="🚨")
        if audit_status["8.3 Design & Development"] == "Minor CAR": st.warning("**Minor CAR on 8.3:** Inconsistent documentation of design review outputs. Action plan required within 30 days.", icon="⚠️")
        st.success("No other major findings noted.", icon="✅")
    with col2:
        st.subheader("AS9100D Clause Review Status")
        st.markdown("- **Why (Actionability):** This demonstrates the hands-on activity of an **AS9100D Lead Auditor**. It provides a clear, actionable summary of the audit's progress and pinpoints the exact areas of the supplier's Quality Management System that are non-compliant and require corrective action (CARs).")
        for clause, status in audit_status.items():
            if status == "Passed": st.markdown(f"- ✅ **{clause}:** `{status}`")
            elif status == "Minor CAR": st.markdown(f"- ⚠️ **{clause}:** `{status}`")
            else: st.markdown(f"- 🚨 **{clause}:** `{status}`")
