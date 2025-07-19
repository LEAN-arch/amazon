import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please return to the 'Global Command Center' home page to initialize the app.")
    st.stop()

# Unpack data
failures = st.session_state['app_data']['failures']
suppliers = st.session_state['app_data']['suppliers']

# --- STATE INITIALIZATION FOR THIS PAGE'S WIDGETS ---
if 'traceability_run' not in st.session_state:
    st.session_state.traceability_run = False
if 'traced_lot_id' not in st.session_state:
    st.session_state.traced_lot_id = ""

# --- UI RENDER ---
st.markdown("# 🔧 Failure Analysis & Root Cause System (FRACAS)")
st.markdown("This hub is the engine for our closed-loop quality system, integrating statistical analysis, root cause drill-down, and traceability to drive continuous improvement in line with **ISO 9001/AS9100** corrective action principles.")

st.subheader("1. Failure Rate Statistical Process Control (p-Chart)")
st.markdown("""
- **What:** A p-Chart monitoring the proportion of defective ASIC units over time, plotted against statistically calculated Upper and Lower Control Limits (UCL/LCL).
- **Why (Actionability):** This is a direct implementation of the JD's requirement for **"early detection of process excursions"** as per **AS9100D Clause 9.1.1**. A point outside the red control limits is a statistically significant signal (a "special cause") that the process has changed. This is an unambiguous, data-driven trigger to **launch an 8D investigation**.
""")

@st.cache_data
def generate_spc_data():
    np.random.seed(42); lots = pd.DataFrame({'lot_id': [f"L-{100+i}" for i in range(25)], 'inspection_date': pd.to_datetime(pd.date_range(start='2023-08-01', periods=25)), 'lot_size': np.random.randint(1000, 1500, size=25)})
    base_defects = np.random.randint(5, 15, size=25); base_defects[10] = 35; base_defects[21] = 42
    lots['defects'] = base_defects; lots['p'] = lots['defects'] / lots['lot_size']; return lots

spc_df = generate_spc_data()
p_bar = spc_df['defects'].sum() / spc_df['lot_size'].sum(); n_bar = spc_df['lot_size'].mean()
ucl = p_bar + 3 * np.sqrt((p_bar * (1 - p_bar)) / n_bar); lcl = max(0, p_bar - 3 * np.sqrt((p_bar * (1 - p_bar)) / n_bar))
spc_df['ooc'] = (spc_df['p'] > ucl) | (spc_df['p'] < lcl)

fig_spc = go.Figure()
fig_spc.add_trace(go.Scatter(x=spc_df['inspection_date'], y=spc_df['p'], mode='lines+markers', name='Proportion Defective'))
fig_spc.add_trace(go.Scatter(x=spc_df[spc_df['ooc']]['inspection_date'], y=spc_df[spc_df['ooc']]['p'], mode='markers', name='Out of Control', marker=dict(color='red', size=12, symbol='x')))
fig_spc.add_hline(y=p_bar, line=dict(dash="dash", color="green"), name="Center Line (Avg)"); fig_spc.add_hline(y=ucl, line=dict(dash="dot", color="red"), name="UCL"); fig_spc.add_hline(y=lcl, line=dict(dash="dot", color="red"), name="LCL")
fig_spc.update_layout(title="p-Chart for Incoming ASIC Defect Rate", yaxis_title="Proportion Defective", yaxis_tickformat=".2%", xaxis_title="Inspection Date", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_spc, use_container_width=True, key="p_chart_failures")

st.divider()

tab_rca, tab_8d, tab_cl = st.tabs(["2. Root Cause Analysis (RCA) Drill-Down", "3. 8D Investigation & Traceability", "Closed-Loop Visualizer"])
with tab_rca:
    st.subheader("2. Interactive Root Cause Analysis Dashboard")
    st.markdown("""
    - **What:** A Sunburst chart providing a hierarchical view of our quality issues, from the symptom (Failure Mode) down to the diagnosed underlying cause (Root Cause).
    - **How:** Data is aggregated from completed 8D investigations. The chart visualizes the parent-child relationship between failure modes and their contributing root causes, organized by supply chain stage (Fab, Assembly, Test).
    - **Why (Actionability):** This powerful visual moves beyond just counting failures to analyzing their systemic origins, a principle central to **IATF 16949** and **JEDEC JEP143** (IC Failure Analysis). It allows us to focus corrective actions on the biggest drivers. For example, seeing that most **Assembly Defects** are due to 'Wire Bond' issues points to a systemic need for supplier training or specification control based on **IPC** standards.
    """)
    @st.cache_data
    def get_rca_data():
        return pd.DataFrame([
            {'Stage': 'Assembly Defect', 'Failure_Mode': 'Wire Bond', 'Root_Cause': 'Incorrect Bonding Parameter'},
            {'Stage': 'Assembly Defect', 'Failure_Mode': 'Wire Bond', 'Root_Cause': 'Pad Contamination'},
            {'Stage': 'Assembly Defect', 'Failure_Mode': 'Die Attach', 'Root_Cause': 'Epoxy Voiding'},
            {'Stage': 'Fab Defect', 'Failure_Mode': 'Parametric Drift', 'Root_Cause': 'Vt Mismatch'},
            {'Stage': 'Fab Defect', 'Failure_Mode': 'Parametric Drift', 'Root_Cause': 'Gate Oxide Leakage'},
            {'Stage': 'Fab Defect', 'Failure_Mode': 'Yield Loss', 'Root_Cause': 'Photolithography Hotspot'},
            {'Stage': 'Test Escape', 'Failure_Mode': 'At-Speed Failure', 'Root_Cause': 'Test Program Hole'},
            {'Stage': 'Test Escape', 'Failure_Mode': 'At-Speed Failure', 'Root_Cause': 'Tester-to-Tester Variation'},
        ])
    rca_df = get_rca_data()
    fig_sunburst = px.sunburst(rca_df, path=['Stage', 'Failure_Mode', 'Root_Cause'], title="Interactive RCA Drill-Down of Closed Investigations", height=600)
    st.plotly_chart(fig_sunburst, use_container_width=True, key="sunburst_rca")
    st.info("Click on a segment in the inner ring to drill down into its root causes.", icon="💡")

with tab_8d:
    st.subheader("3. 8D Investigation Workflow with Device Traceability")
    st.markdown("""
    - **Why (Actionability):** This directly demonstrates the JD's requirement to be a **\"subject matter expert in device traceability.\"** By linking a failure back to its specific production lot and process data (as mandated by standards like **IPC-1782**), the root cause investigation is accelerated, providing immediate, actionable context to the 8D team.
    """)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with st.form("8d_form_enhanced"):
            st.text_input("Part Number", "KU-ASIC-COM-001"); 
            st.selectbox("Supplier", suppliers['Supplier'].unique())
            lot_id_input = st.text_input("Wafer / Assembly Lot ID", "A-LOT-7891", help="Enter a Lot ID to retrieve historical process data.")
            st.text_area("Problem Description (D2)", f"During OQC, 5 devices from Lot {lot_id_input} showed wire bond shorts on Pins 12-14.")
            st.multiselect("Team Members (D1)", ["J. Doe (SQE)", "S. Smith (Design)", "R. Chen (Supplier Quality)"]); submitted = st.form_submit_button("Launch Investigation & Trace Lot")
            if submitted:
                st.session_state.traceability_run = True
                st.session_state.traced_lot_id = lot_id_input
    with col2:
        st.markdown("##### ASIC Traceability & Process Context"); 
        st.caption("Data associated with the entered Lot ID appears here.")
        if st.session_state.traceability_run:
            with st.container(border=True):
                st.success(f"**Traceability Data Found for Lot {st.session_state.traced_lot_id}:**")
                # --- ASIC SME Enhancement: Detailed Traceability Data ---
                st.markdown(f"""
                - **Assembly Date Code:** `2341` (Week 41, 2023)
                - **Test Program Version:** `v2.3.1_release`
                - **Upstream Wafer Lot:** `GW-WN45B-07`
                - **Source Foundry:** `Global Wafer Inc.`
                """)
                st.metric("Final Test Yield for this Lot", "97.3%", delta="-2.2% vs. Avg", delta_color="inverse")
                st.markdown("**Associated Wafer Acceptance Test (WAT) Data for Wafer Lot GW-WN45B-07:**")
                np.random.seed(hash(st.session_state.traced_lot_id) % (2**32 - 1))
                vt_mean = np.random.normal(0.45, 0.005)
                st.text(f"- Avg. Threshold Voltage (Vt): {vt_mean:.3f}V (Nominal)")
                st.warning("- Avg. Gate Leakage (Ig): 1.2nA (Marginal High)")
                st.markdown("**Insight:** The marginal gate leakage from the source wafer lot could be a contributing factor to the downstream failures, pointing the investigation towards the foundry process.")

with tab_cl:
    st.subheader("Closed-Loop Mechanism Visualizer")
    st.markdown("- **Why:** This chart is a powerful communication tool that visually explains the strategic goal of an integrated quality system: a problem detected at an OSAT (left) should trigger an analysis that drives a corrective action at the foundry (right), resulting in improved quality.")
    fig_sankey = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=["OSAT Test Failures (High DPPM)", "Foundry Process Drift", "Improved OSAT Yield", "Failure Analysis (RCA)", "Foundry CAPA", "Wafer Parametric Data"], color=["red", "orange", "green", "blue", "blue", "blue"]), link=dict(source=[0, 1, 3, 3, 4], target=[3, 3, 4, 5, 2], value=[10, 5, 8, 4, 12]))])
    fig_sankey.update_layout(title_text="Example: OSAT Test Failure -> Foundry Corrective Action", font_size=12)
    st.plotly_chart(fig_sankey, use_container_width=True, key="sankey_diagram")
