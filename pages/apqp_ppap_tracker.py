import streamlit as st
import pandas as pd
import plotly.figure_factory as ff

st.set_page_config(layout="wide", page_title="APQP/PPAP Tracker", page_icon="📋")

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please go to the 'Global Command Center' home page to initialize the app.")
    st.stop()

apqp_data = st.session_state['app_data']['apqp_data']

# --- UI RENDER ---
st.markdown("# 📋 APQP / PPAP Tracker (AS9145)")
st.markdown("Manage New Product Introduction quality planning for all active ASIC projects.")

st.subheader("NPI Project Timelines (Gantt Chart)")
st.markdown("""
- **What:** A Gantt chart visualizing the start and end dates for each NPI (New Product Introduction) project.
- **How:** Created directly from the APQP data's start and finish dates for each part number.
- **Why (Actionability):** This provides a high-level program management view of all NPI project schedules. It allows the SQE to instantly spot potential resource conflicts, identify projects that are at risk of delay, and manage stakeholder expectations.
""")
gantt_df = apqp_data.rename(columns={'Part_Number': 'Task', 'Start': 'Start', 'Finish': 'Finish', 'Status': 'Resource'})
fig_gantt = ff.create_gantt(gantt_df, index_col='Resource', show_colorbar=True, group_tasks=True, title="Project Timelines")
st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_chart")

st.divider()

st.subheader("APQP Stage Kanban Board")
st.markdown("""
- **What:** A Kanban-style board showing which NPI projects are in each of the five APQP (Advanced Product Quality Planning) phases.
- **How:** Projects are sorted into columns based on their current 'Stage' status in the data.
- **Why (Actionability):** This visualizes the flow of parts through the entire NPI quality process. It makes it easy to spot bottlenecks (e.g., many parts stuck in 'Validation') and manage the overall NPI portfolio health.
""")
phases = ['1. Planning', '2. Product Design', '3. Process Design', '4. Validation', '5. Production']

cols = st.columns(len(phases))
for i, phase in enumerate(phases):
    with cols[i]:
        st.subheader(phase)
        parts_in_phase = apqp_data[apqp_data['Stage'] == phase]
        for index, part in parts_in_phase.iterrows():
            status_icon = "🟢" if part['Status'] == 'On Track' else ("🟠" if part['Status'] == 'At Risk' else "✅")
            with st.container(border=True):
                st.markdown(f"**{part['Part_Number']}**")
                st.markdown(f"Status: **{part['Status']}** {status_icon}")
                st.caption(f"Owner: {part['Owner']}")
