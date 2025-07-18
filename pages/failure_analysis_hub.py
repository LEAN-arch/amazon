import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Failure Analysis Hub", page_icon="🔧")

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please go to the 'Global Command Center' home page to initialize the app.")
    st.stop()

failures = st.session_state['app_data']['failures']
suppliers = st.session_state['app_data']['suppliers']

# --- UI RENDER ---
st.markdown("# 🔧 Failure Analysis (FRACAS) Hub")
st.markdown("A central system for Failure Reporting, Analysis, and Corrective Action. This is the core of our closed-loop quality system.")

st.subheader("Failure Trends Over Time")
st.markdown("""
- **What:** An area chart showing the number of reported failures per month, broken down by failure mode.
- **How:** The failure data is grouped by month and failure type, then plotted over time.
- **Why (Actionability):** This chart helps identify systemic issues. A sudden spike in a specific failure mode (e.g., 'Wire Bond Lift') points to a recent process change or excursion that needs immediate investigation. Conversely, a decreasing trend after a corrective action visually confirms its effectiveness.
""")
failures['Month'] = failures['Date_Reported'].dt.to_period('M').astype(str)
trend_data = failures.groupby(['Month', 'Failure_Mode']).size().reset_index(name='Count')
fig_trend = px.area(trend_data, x='Month', y='Count', color='Failure_Mode', title="Monthly Failure Reports by Type")
st.plotly_chart(fig_trend, use_container_width=True, key="failure_trend_chart")

st.divider()

tab1, tab2, tab3 = st.tabs(["Open Failures", "Launch New 8D/DMAIC", "Closed-Loop Mechanism Visualizer"])

with tab1:
    st.subheader("Active Failure Investigations")
    st.markdown("- **What:** A filterable table of all quality issues that are not yet 'Closed'. \n- **Why:** This is the SQE's daily work queue, showing all problems that require active management.")
    open_failures = failures[failures['Status'] != 'Closed']
    st.dataframe(open_failures, use_container_width=True)

with tab2:
    st.subheader("Initiate Structured Problem Solving (8D)")
    st.info("The 8D process ensures a thorough and documented approach to root cause analysis and corrective action.")
    with st.form("8d_form"):
        st.text_input("Part Number", "KU-ASIC-COM-001")
        st.selectbox("Supplier", suppliers['Supplier'].unique())
        st.text_area("Problem Description (D2)", "During OQC, 5 devices from Lot #KUI-7891 showed lifted wire bonds on Pad 14.")
        st.text_area("Interim Containment Action (D3)", "Placed Lot #KUI-7891 on hold. Screened all remaining units from the wafer lot. Segregated suspect units.")
        st.multiselect("Team Members (D1)", ["J. Doe (SQE)", "S. Smith (Design)", "R. Chen (Supplier Quality)"])
        submitted = st.form_submit_button("Launch Investigation")
        if submitted:
            st.success("New Failure Analysis FA-006 has been created and assigned.")

with tab3:
    st.subheader("Visualizing the Closed-Loop Mechanism")
    st.markdown("""
    - **What:** A Sankey diagram illustrating the ideal flow of information in our quality system.
    - **How:** It shows hypothetical volumes of data flowing between stages.
    - **Why (Actionability):** This chart is a powerful communication tool. It visually explains the goal of an integrated quality system: a problem detected at an OSAT (left) should trigger a failure analysis, which identifies a root cause at the foundry, leading to a corrective action (CAPA) that ultimately results in improved yield (right). It demonstrates a strategic understanding of quality systems.
    """)
    fig_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15, thickness=20, line=dict(color="black", width=0.5),
            label=["OSAT Test Failures (High DPPM)", "Foundry Process Drift", "Improved OSAT Yield", "Failure Analysis (RCA)", "Foundry CAPA", "Wafer Parametric Data"],
            color=["red", "orange", "green", "blue", "blue", "blue"]
        ),
        link=dict(source=[0, 1, 3, 3, 4], target=[3, 3, 4, 5, 2], value=[10, 5, 8, 4, 12])
    )])
    fig_sankey.update_layout(title_text="Example: OSAT Test Failure -> Foundry Corrective Action", font_size=12)
    st.plotly_chart(fig_sankey, use_container_width=True, key="sankey_diagram")
