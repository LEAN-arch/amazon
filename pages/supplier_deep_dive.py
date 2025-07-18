import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Supplier Deep Dive", page_icon="🔬")

# Check if data is loaded
if 'data_loaded' not in st.session_state:
    st.error("Data not loaded. Please go to the main page first.")
    st.stop()

# Load data
suppliers = st.session_state['suppliers']
perf_df = st.session_state['performance_data']

st.markdown("# 🔬 Supplier Deep Dive")
st.markdown("Analyze individual supplier performance, review process control data, and track traceability.")

# --- Supplier Selection ---
selected_supplier = st.selectbox(
    "Select a Supplier to Analyze",
    suppliers['Supplier'].unique()
)

# Filter data for the selected supplier
supplier_data = perf_df[perf_df['Supplier'] == selected_supplier]
supplier_info = suppliers[suppliers['Supplier'] == selected_supplier].iloc[0]

# --- Supplier Info & Performance ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Performance: {selected_supplier}")
    fig_yield = go.Figure()
    fig_yield.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['Yield'], mode='lines', name='Yield'))
    fig_yield.update_layout(title="Yield Trend", yaxis_title="Yield (%)", yaxis_tickformat=".2%")
    st.plotly_chart(fig_yield, use_container_width=True)

with col2:
    st.subheader(f"Type: {supplier_info['Type']}")
    fig_dppm = go.Figure()
    fig_dppm.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['DPPM'], mode='lines', name='DPPM', line=dict(color='red')))
    fig_dppm.update_layout(title="Defects Per Million (DPPM) Trend", yaxis_title="DPPM")
    st.plotly_chart(fig_dppm, use_container_width=True)

st.divider()

# --- SPC & Traceability ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Statistical Process Control (SPC) Chart")
    st.caption("Simulated data for a critical process parameter (e.g., Gate Oxide Thickness)")
    
    # Generate mock SPC data
    np.random.seed(42)
    target = 10.0
    ucl = 10.5
    lcl = 9.5
    spc_data = np.random.normal(loc=target, scale=0.15, size=50)
    # Add an excursion
    spc_data[30:35] += 0.6
    
    fig_spc = go.Figure()
    fig_spc.add_trace(go.Scatter(y=spc_data, mode='lines+markers', name='Measurement'))
    fig_spc.add_hline(y=target, line_dash="dash", line_color="green", annotation_text="Target")
    fig_spc.add_hline(y=ucl, line_dash="dot", line_color="red", annotation_text="UCL")
    fig_spc.add_hline(y=lcl, line_dash="dot", line_color="red", annotation_text="LCL")
    
    # Highlight OOC points
    ooc_points = [i for i, val in enumerate(spc_data) if val > ucl or val < lcl]
    fig_spc.add_trace(go.Scatter(x=ooc_points, y=spc_data[ooc_points], mode='markers', marker=dict(color='red', size=10, symbol='x'), name='Out of Control'))

    st.plotly_chart(fig_spc, use_container_width=True)

with col2:
    st.subheader("Device Traceability & Action Items")
    with st.expander("📝 Open Action Items for this Supplier"):
        supplier_failures = st.session_state['failures'][st.session_state['failures']['Supplier'] == selected_supplier]
        st.dataframe(supplier_failures)

    st.text_input("Enter Lot Number to Trace", placeholder="e.g., KUI-7891-A")
    if st.button("Trace Lot"):
        st.success(f"**Traceability Path for KUI-7891-A:**")
        st.markdown(f"""
        - **OSAT:** {selected_supplier}, Final Test Date: 2023-09-12
        - **Wafer Lot:** WAF-GWI-23-07B
        - **Foundry:** Global Wafer Inc.
        - **Fab Start Date:** 2023-07-15
        """)
