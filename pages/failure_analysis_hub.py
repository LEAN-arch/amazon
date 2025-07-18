import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Failure Analysis Hub", page_icon="🔧")

# Check if data is loaded
if 'data_loaded' not in st.session_state:
    st.error("Data not loaded. Please go to the main page first.")
    st.stop()

failures = st.session_state['failures']

st.markdown("# 🔧 Failure Analysis (FRACAS) Hub")
st.markdown("A central system for Failure Reporting, Analysis, and Corrective Action.")

tab1, tab2, tab3 = st.tabs(["Open Failures", "Launch New 8D/DMAIC", "Closed-Loop Mechanism Visualizer"])

with tab1:
    st.subheader("Active Failure Investigations")
    open_failures = failures[failures['Status'] != 'Closed']
    st.dataframe(open_failures, use_container_width=True)

with tab2:
    st.subheader("Initiate Structured Problem Solving")
    st.info("Use this form to launch a new 8D or DMAIC investigation for a quality event.")
    with st.form("8d_form"):
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
    st.markdown("This demonstrates how OSAT data is used to drive foundry process improvements, improving yield and quality.")
    
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = ["OSAT Test Failures (High DPPM)", "Foundry Process Drift", "Improved OSAT Yield", "Failure Analysis (RCA)", "Foundry CAPA", "Wafer Parametric Data"],
          color = ["red", "orange", "green", "blue", "blue", "blue"]
        ),
        link = dict(
          source = [0, 1, 3, 3, 4], 
          target = [3, 3, 4, 5, 2],
          value = [10, 5, 8, 4, 12]
      ))])

    fig.update_layout(title_text="Example: OSAT Test Failure -> Foundry Corrective Action", font_size=12)
    st.plotly_chart(fig, use_container_width=True)
