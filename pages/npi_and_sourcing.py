import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="NPI & Sourcing", page_icon="🚀")

st.markdown("# 🚀 NPI & 2nd Source Qualification")
st.markdown("Monitor the pipeline for new supplier onboarding and use data to make strategic sourcing decisions.")

# Mock data for NPI pipeline and sourcing
npi_data = {
    'Supplier': ['Future Foundries LLC', 'Global Test Solutions', 'NextGen Packaging', 'AeroChip Test'],
    'Part_Type': ['RF ASIC', 'Power Mgmt ASIC', 'Memory Controller', 'Power Mgmt ASIC'],
    'Stage': ['2. Initial Audit', '4. Reliability Testing', '1. Discovery', '5. Full Qualification'],
    'Audit_Score': [85, 92, 78, 95],
    'Quoted_Cost': [2.50, 1.80, 1.50, 2.10],
    'Risk': ['Medium', 'Low', 'Medium', 'Low']
}
npi_df = pd.DataFrame(npi_data)

st.subheader("Strategic Sourcing Matrix")
st.info("This plot visualizes the trade-off between supplier quality (Audit Score) and cost. The ideal partner is in the top-left quadrant (High Quality, Low Cost). This helps in negotiations and final selection.", icon="🎯")

fig_scatter = px.scatter(npi_df, 
                         x='Quoted_Cost', 
                         y='Audit_Score',
                         size='Audit_Score',
                         color='Risk',
                         hover_name='Supplier',
                         text='Supplier',
                         title="Quality vs. Cost Analysis for Potential Suppliers",
                         labels={'Quoted_Cost': 'Quoted Cost per Unit ($)', 'Audit_Score': 'Qualification Audit Score'})
fig_scatter.update_traces(textposition='top center')
fig_scatter.add_vline(x=npi_df['Quoted_Cost'].mean(), line_dash="dash", annotation_text="Avg. Cost")
fig_scatter.add_hline(y=npi_df['Audit_Score'].mean(), line_dash="dash", annotation_text="Avg. Score")
st.plotly_chart(fig_scatter, use_container_width=True)

st.divider()

st.subheader("Qualification Kanban Pipeline")
st.caption("Track the progress of each potential supplier through the qualification stages.")
stages = ['1. Discovery', '2. Initial Audit', '3. Sample Evaluation', '4. Reliability Testing', '5. Full Qualification']
# Kanban board code remains the same as before...
