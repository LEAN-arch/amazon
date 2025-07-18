import streamlit as st
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please return to the 'Global Command Center' home page to initialize the app.")
    st.stop()

apqp_data = st.session_state['app_data']['apqp_data']

# --- UI RENDER ---
st.markdown("# 📋 APQP / PPAP Project Hub (AS9145)")
st.markdown("This hub provides a multi-level view for managing New Product Introduction (NPI) quality, from high-level portfolio timelines to deep dives into individual PPAP element reviews.")

tab_portfolio, tab_deepdive = st.tabs(["Portfolio View (Timeline & Kanban)", "PPAP Element Deep Dive"])

# ==============================================================================
# TAB 1: Portfolio View
# ==============================================================================
with tab_portfolio:
    st.header("NPI Portfolio Management")
    st.subheader("Project Timelines (Gantt Chart)")
    st.markdown("""
    - **What:** A Gantt chart visualizing the start and end dates for each NPI project.
    - **Why (Actionability):** This provides a program management view of all NPI project schedules, allowing the SQE to instantly spot potential resource conflicts, identify projects at risk of delay, and manage stakeholder expectations.
    """)
    gantt_df = apqp_data.rename(columns={'Part_Number': 'Task', 'Start': 'Start', 'Finish': 'Finish', 'Status': 'Resource'})
    fig_gantt = ff.create_gantt(gantt_df, index_col='Resource', show_colorbar=True, group_tasks=True, title="Project Timelines")
    st.plotly_chart(fig_gantt, use_container_width=True, key="gantt_chart")

    st.divider()

    st.subheader("APQP Stage Kanban Board")
    st.markdown("""
    - **What:** A Kanban-style board showing which NPI projects are in each of the five APQP (Advanced Product Quality Planning) phases.
    - **Why (Actionability):** This visualizes the flow of parts through the entire NPI quality process, making it easy to spot bottlenecks (e.g., many parts stuck in 'Validation') and manage the overall NPI portfolio health.
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

# ==============================================================================
# TAB 2: PPAP Element Deep Dive
# ==============================================================================
with tab_deepdive:
    st.header("PPAP Submission Review Workspace")
    st.markdown("Select a part number to review the status of its individual PPAP elements and associated risk analysis documents.")
    
    selected_part = st.selectbox("Select Part Number for Deep Dive", apqp_data['Part_Number'].unique(), key="part_select_ppap")
    part_details = apqp_data[apqp_data['Part_Number'] == selected_part].iloc[0]
    st.info(f"**Viewing PPAP for:** `{part_details['Part_Number']}` | **Supplier:** `{part_details['Supplier']}` | **Current Stage:** `{part_details['Stage']}`")

    st.subheader("PPAP Element Checklist")
    st.markdown("""
    - **What:** A detailed checklist tracking the submission and approval status of the 18 core PPAP elements.
    - **Why:** This transforms the tool into an active workspace for the SQE. It demonstrates a deep, practical understanding of the PPAP process beyond high-level tracking. The references to standards like **IATF 16949** show broad quality systems knowledge.
    """)
    ppap_elements = [
        {"Element": "Design Records", "Reference": "AS9145 / IATF", "Status": "Approved"},
        {"Element": "Engineering Change Documents", "Reference": "AS9145 / IATF", "Status": "Approved"},
        {"Element": "Process Flow Diagram", "Reference": "AS9145 / IATF", "Status": "Submitted"},
        {"Element": "Process FMEA (PFMEA)", "Reference": "AS9145 / IATF", "Status": "Submitted"},
        {"Element": "Control Plan", "Reference": "AS9145 / IATF", "Status": "Submitted"},
        {"Element": "Measurement System Analysis (MSA)", "Reference": "AS9145 / IATF", "Status": "Rejected"},
        {"Element": "Dimensional Results", "Reference": "AS9145 / IATF", "Status": "Approved"},
        {"Element": "Initial Process Studies (Cpk)", "Reference": "AS9145 / IATF", "Status": "Submitted"},
        {"Element": "Part Submission Warrant (PSW)", "Reference": "AS9145 / IATF", "Status": "Not Submitted"},
    ]
    ppap_df = pd.DataFrame(ppap_elements)
    def style_status(df):
        def color_status(val):
            if val == "Approved": color = 'mediumseagreen'
            elif val == "Submitted": color = 'orange'
            elif val == "Rejected": color = 'indianred'
            else: color = 'lightgrey'
            return f'background-color: {color}; color: white' if val != "Not Submitted" else ''
        return df.style.map(color_status, subset=['Status'])
    st.dataframe(style_status(ppap_df), use_container_width=True)

    st.divider()
    
    st.subheader("SME Deep Dive: Core Quality Document Analysis")
    st.markdown("This section provides a summary of the critical risk and measurement analysis documents that underpin the PPAP submission.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Process FMEA Summary")
        st.markdown("""
        - **What:** A summary of the highest-risk process steps identified in the Process Failure Mode and Effects Analysis.
        - **Why (Actionability):** PFMEA is a proactive risk assessment tool. A high **Risk Priority Number (RPN)** flags process steps that require robust mitigation in the Control Plan. An SQE must review this to ensure the supplier has adequately addressed all high-risk failure modes before approving the process.
        """)
        pfmea_data = {
            "Process Step": ["Wire Bonding", "Die Attach", "Encapsulation"],
            "Severity (S)": [9, 10, 6],
            "Occurrence (O)": [3, 2, 4],
            "Detection (D)": [5, 6, 3],
        }
        pfmea_df = pd.DataFrame(pfmea_data)
        # --- THIS IS THE CORRECTED LINE ---
        pfmea_df["RPN"] = pfmea_df["Severity (S)"] * pfmea_df["Occurrence (O)"] * pfmea_df["Detection (D)"]
        st.dataframe(
            pfmea_df.sort_values("RPN", ascending=False), 
            use_container_width=True,
            column_config={"RPN": st.column_config.ProgressColumn("RPN", min_value=0, max_value=1000)}
        )

    with col2:
        st.markdown("##### Measurement System Analysis (Gage R&R)")
        st.markdown("""
        - **What:** A summary of a Gage Repeatability & Reproducibility (Gage R&R) study for a critical inspection.
        - **Why (Actionability):** An MSA answers the question: "Is our measurement system trustworthy?" If the measurement system has too much variation (a high % Contribution), we cannot trust our inspection data. A rejected MSA (as shown here, >9%) is a valid reason to **reject a PPAP** and demand the supplier fix their measurement process first.
        """)
        gage_results = {"Source of Variation": ["Repeatability (EV)", "Reproducibility (AV)", "Total Gage R&R", "Part-to-Part"], "% Contribution": [7.5, 4.2, 11.7, 88.3]}
        gage_df = pd.DataFrame(gage_results)
        total_grr = gage_df[gage_df["Source of Variation"] == "Total Gage R&R"]["% Contribution"].iloc[0]
        fig_gage = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = total_grr,
            title = {'text': "Total Gage R&R (% Contribution)"},
            gauge = {
                'axis': {'range': [None, 30]}, 'bar': {'color': "darkblue"},
                'steps': [{'range': [0, 1], 'color': 'green'}, {'range': [1, 9], 'color': 'yellow'}, {'range': [9, 30], 'color': 'red'}],
                'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 9}}
        ))
        st.plotly_chart(fig_gage, use_container_width=True, key="gage_r_and_r")
        if total_grr > 9:
            st.error(f"**MSA Rejected:** Total Gage R&R of {total_grr}% exceeds the >9% threshold for rejection. The measurement system is not acceptable.", icon="🚨")
        else:
            st.success("MSA Acceptable.")
