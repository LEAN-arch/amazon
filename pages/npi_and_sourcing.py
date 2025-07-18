import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="NPI & Sourcing", page_icon="🚀")

st.markdown("# 🚀 NPI & 2nd Source Qualification")
st.markdown("Monitor the pipeline for new supplier onboarding and 2nd source qualifications to ensure supply chain resiliency.")

# Mock data for NPI pipeline
npi_data = {
    'Supplier': ['Future Foundries LLC', 'Global Test Solutions', 'NextGen Packaging'],
    'Part_Type': ['RF ASIC', 'Power Mgmt ASIC', 'Memory Controller'],
    'Stage': ['2. Initial Audit', '4. Reliability Testing', '1. Discovery'],
    'Next_Milestone': ['On-site Audit Q4', 'Complete 1000hr HTOL', 'Sign NDA'],
    'Risk': ['Low', 'Medium', 'Low']
}
npi_df = pd.DataFrame(npi_data)

st.subheader("Qualification Pipeline")

# --- KANBAN STYLE FOR NPI ---
stages = ['1. Discovery', '2. Initial Audit', '3. Sample Evaluation', '4. Reliability Testing', '5. Full Qualification']
cols = st.columns(len(stages))

for i, stage in enumerate(stages):
    with cols[i]:
        st.subheader(stage)
        suppliers_in_stage = npi_df[npi_df['Stage'] == stage]
        for index, supplier in suppliers_in_stage.iterrows():
            risk_color = "green" if supplier['Risk'] == 'Low' else ('orange' if supplier['Risk'] == 'Medium' else 'red')
            with st.container(border=True):
                st.markdown(f"**{supplier['Supplier']}**")
                st.caption(f"Part: {supplier['Part_Type']}")
                st.markdown(f"Risk: <font color='{risk_color}'>{supplier['Risk']}</font>", unsafe_allow_html=True)
                st.write(f"Next Step: {supplier['Next_Milestone']}")

st.divider()

st.subheader("Comparative Analysis Tool (Example)")
st.info("Select two potential suppliers for a side-by-side comparison of qualification data.")

col1, col2 = st.columns(2)

with col1:
    st.selectbox("Select Primary Supplier", ["AeroChip Test", "Global Test Solutions"], key="s1")
    st.metric("Audit Score", "95/100")
    st.metric("Sample Yield", "99.8%")
    st.metric("Quoted Cost/Unit", "$1.25")

with col2:
    st.selectbox("Select Secondary Supplier", ["Global Test Solutions", "AeroChip Test"], key="s2")
    st.metric("Audit Score", "88/100")
    st.metric("Sample Yield", "99.6%")
    st.metric("Quoted Cost/Unit", "$1.18")
