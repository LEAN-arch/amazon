import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="APQP/PPAP Tracker", page_icon="📋")

# Check if data is loaded
if 'data_loaded' not in st.session_state:
    st.error("Data not loaded. Please go to the main page first.")
    st.stop()
    
apqp_data = st.session_state['apqp_data']

st.markdown("# 📋 APQP / PPAP Tracker (AS9145)")
st.markdown("Manage New Product Introduction quality planning using a Kanban-style board.")
st.info("This board visualizes the progress of each new ASIC part number through the key phases of Advanced Product Quality Planning.")

# --- KANBAN BOARD ---
phases = [
    '1. Planning', 
    '2. Product Design', 
    '3. Process Design', 
    '4. Validation', 
    '5. Production'
]

cols = st.columns(len(phases))

for i, phase in enumerate(phases):
    with cols[i]:
        st.subheader(phase)
        # Filter parts for the current phase
        parts_in_phase = apqp_data[apqp_data['Stage'] == phase]
        for index, part in parts_in_phase.iterrows():
            status_icon = "🟢" if part['Status'] == 'On Track' else ("🟠" if part['Status'] == 'At Risk' else "✅")
            with st.container(border=True):
                st.markdown(f"**{part['Part_Number']}**")
                st.markdown(f"{status_icon} Status: **{part['Status']}**")
                st.caption(f"Owner: {part['Owner']}")
                with st.expander("Show PPAP Elements"):
                    st.write("""
                    - **Design Records:** ✅ Approved
                    - **Process Flow Diagram:** 💬 Submitted
                    - **Process FMEA:** 📝 In Progress
                    - **Control Plan:** 📝 In Progress
                    - **MSA / Gage R&R:** 🚫 Not Started
                    - **Initial Process Studies:** 🚫 Not Started
                    - **Part Submission Warrant (PSW):** 🚫 Not Started
                    """)
