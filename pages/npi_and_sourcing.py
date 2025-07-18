import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="NPI & Sourcing", page_icon="🚀")

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please go to the 'Global Command Center' home page to initialize the app.")
    st.stop()

# --- UI RENDER ---
st.markdown("# 🚀 NPI & 2nd Source Qualification")
st.markdown("Monitor the pipeline for new supplier onboarding and use data to make strategic sourcing decisions.")

# --- CORRECTED DATA ---
# The 'Next_Milestone' column has been added to this dictionary to fix the KeyError.
npi_data = {
    'Supplier': ['Future Foundries LLC', 'Global Test Solutions', 'NextGen Packaging', 'AeroChip Test'],
    'Part_Type': ['RF ASIC', 'Power Mgmt ASIC', 'Memory Controller', 'Power Mgmt ASIC'],
    'Stage': ['2. Initial Audit', '4. Reliability Testing', '1. Discovery', '5. Full Qualification'],
    'Audit_Score': [85, 92, 78, 95], 
    'Quoted_Cost': [2.50, 1.80, 1.50, 2.10], 
    'Risk': ['Medium', 'Low', 'Medium', 'Low'],
    'Next_Milestone': ['On-site Audit Q4', 'Complete 1000hr HTOL', 'Sign NDA', 'Production Ramp'] # THIS WAS THE MISSING DATA
}
npi_df = pd.DataFrame(npi_data)

st.subheader("Strategic Sourcing Matrix")
st.info("This plot visualizes the trade-off between supplier quality (Audit Score) and cost. The ideal partner is in the top-left quadrant (High Quality, Low Cost). This helps in negotiations and final selection.", icon="🎯")

fig_scatter = px.scatter(
    npi_df, x='Quoted_Cost', y='Audit_Score',
    size='Audit_Score', color='Risk', hover_name='Supplier', text='Supplier',
    title="Quality vs. Cost Analysis for Potential Suppliers",
    labels={'Quoted_Cost': 'Quoted Cost per Unit ($)', 'Audit_Score': 'Qualification Audit Score'}
)
fig_scatter.update_traces(textposition='top center')
fig_scatter.add_vline(x=npi_df['Quoted_Cost'].mean(), line_dash="dash", annotation_text="Avg. Cost")
fig_scatter.add_hline(y=npi_df['Audit_Score'].mean(), line_dash="dash", annotation_text="Avg. Score")
st.plotly_chart(fig_scatter, use_container_width=True, key="sourcing_scatter")

st.divider()

st.subheader("Qualification Kanban Pipeline")
st.caption("Track the progress of each potential supplier through the qualification stages.")
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
                # This line will now work correctly.
                st.write(f"Next Step: {supplier['Next_Milestone']}")
