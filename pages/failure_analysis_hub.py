import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Failure Analysis Hub", page_icon="🔧")

if 'data_loaded' not in st.session_state:
    st.error("Data not loaded. Please go to the main page first.")
    st.stop()

failures = st.session_state['failures']

st.markdown("# 🔧 Failure Analysis (FRACAS) Hub")
st.markdown("A central system for Failure Reporting, Analysis, and Corrective Action. This is the core of our closed-loop quality system.")

st.subheader("Failure Trends Over Time")
st.caption("Tracking failure modes over time helps identify systemic issues or the positive impact of corrective actions.")
failures['Month'] = failures['Date_Reported'].dt.to_period('M').astype(str)
trend_data = failures.groupby(['Month', 'Failure_Mode']).size().reset_index(name='Count')
fig_trend = px.area(trend_data, x='Month', y='Count', color='Failure_Mode', title="Monthly Failure Reports by Type")
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

tab1, tab2, tab3 = st.tabs(["Open Failures", "Launch New 8D/DMAIC", "Closed-Loop Mechanism Visualizer"])

with tab1:
    st.subheader("Active Failure Investigations")
    open_failures = failures[failures['Status'] != 'Closed']
    st.dataframe(open_failures, use_container_width=True)

with tab2:
    st.subheader("Initiate Structured Problem Solving (8D)")
    st.info("The 8D process ensures a thorough and documented approach to root cause analysis and corrective action.")
    with st.form("8d_form"):
        # ... (rest of the form remains the same)
        st.text_input("Part Number", "KU-ASIC-COM-001")
        st.selectbox("Supplier", st.session_state['suppliers']['Supplier'].unique())
        st.text_area("Problem Description (D2)", "During OQC, 5 devices from Lot #KUI-7891 showed lifted wire bonds on Pad 14.")
        st.text_area("Interim Containment Action (D3)", "Placed Lot #KUI-7891 on hold. Screened all remaining units from the wafer lot. Segregated suspect units.")
        st.multiselect("Team Members (D1)", ["J. Doe (SQE)", "S. Smith (Design)", "R. Chen (Supplier Quality)"])
        submitted = st.form_submit_button("Launch Investigation")
        if submitted:
            st.success("New Failure Analysis FA-006 has been created and assigned.")

with tab3:
    st.subheader("Visualizing the Closed-Loop Process")
    st.caption("This Sankey diagram illustrates the ideal flow of information: a problem detected at the OSAT is traced back to the foundry, and a corrective action at the foundry results in improved quality downstream. This is the goal of our integrated quality system.")
    fig_sankey = go.Figure(data=[go.Sankey(...)]) # Sankey chart code is fine as is
    fig_sankey.update_layout(title_text="Example: OSAT Test Failure -> Foundry Corrective Action")
    st.plotly_chart(fig_sankey, use_container_width=True)
