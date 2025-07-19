import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# --- PAGE CONFIGURATION (SET ONLY ONCE IN THE MAIN APP) ---
st.set_page_config(
    page_title="Kuiper SQE Command Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ATOMIC DATA INITIALIZATION FUNCTION (CORRECTED ASIC SME VERSION) ---
@st.cache_data
def generate_data():
    """
    Generates all necessary dataframes, with the correct ASIC-specific data model
    distinguishing between Frontend (Foundry) and Backend (OSAT) suppliers.
    """
    data = {}
    data['suppliers'] = pd.DataFrame({
        'Supplier': ['Global Wafer Inc.', 'Quantum Assembly', 'AeroChip Test', 'Silicon Foundry Corp.', 'PackagePro OSAT'],
        'Type': ['Foundry', 'OSAT', 'OSAT', 'Foundry', 'OSAT'],
        'Location': ['Austin, TX', 'Penang, Malaysia', 'Hsinchu, Taiwan', 'Phoenix, AZ', 'Manila, Philippines'],
        'Health_Score': [92, 78, 95, 85, 65], 'Open_SCARs': [0, 1, 3, 1, 4], 'AS9100D_Cert': ['Yes', 'Yes', 'Yes', 'Yes', 'In Progress']
    })
    
    date_rng = pd.to_datetime(pd.date_range(start='2023-01-01', end='2023-09-30', freq='D'))
    
    # --- Frontend (Foundry) Specific Data ---
    foundry_perf_data = []
    for supplier in ['Global Wafer Inc.', 'Silicon Foundry Corp.']:
        base_yield = 0.96; base_d0 = 0.12
        for date in date_rng:
            yield_val = base_yield + (np.random.rand() * 0.03) - (np.sin(date.dayofyear / 40) * 0.02)
            d0_val = base_d0 + (np.random.rand() * 0.05) + (np.sin(date.dayofyear / 60) * 0.03)
            foundry_perf_data.append([date, supplier, yield_val, d0_val])
    # THIS IS THE KEY FIX: The key is now correctly 'foundry_perf'
    data['foundry_perf'] = pd.DataFrame(foundry_perf_data, columns=['Date', 'Supplier', 'Wafer_Sort_Yield', 'Defect_Density_D0'])

    # --- Backend (OSAT) Specific Data ---
    osat_perf_data = []
    for supplier in ['Quantum Assembly', 'AeroChip Test', 'PackagePro OSAT']:
        base_fty = 0.99; base_assy_yield = 0.995; base_dppm = 75
        for date in date_rng:
            fty_val = base_fty - (np.random.rand() * 0.02)
            assy_yield_val = base_assy_yield - (np.random.rand() * 0.005)
            dppm_val = base_dppm + np.random.randint(-20, 60)
            osat_perf_data.append([date, supplier, fty_val, assy_yield_val, dppm_val])
    # THIS IS THE KEY FIX: The key is now correctly 'osat_perf'
    data['osat_perf'] = pd.DataFrame(osat_perf_data, columns=['Date', 'Supplier', 'Final_Test_Yield', 'Assembly_Yield', 'DPPM'])
    data['osat_perf'].loc[(data['osat_perf']['Supplier'] == 'PackagePro OSAT') & (data['osat_perf']['Date'] > '2023-08-15'), 'DPPM'] += 150

    # --- ASIC-Specific Failure Modes ---
    data['failures'] = pd.DataFrame({
        'Failure_ID': ['FA-001', 'FA-002', 'FA-003', 'FA-004', 'FA-005', 'FA-006'], 
        'Part_Number': ['KU-ASIC-COM-001', 'KU-ASIC-PWR-003', 'KU-ASIC-COM-001', 'KU-ASIC-RF-002', 'KU-ASIC-PWR-003', 'KU-ASIC-RF-002'],
        'Supplier': ['PackagePro OSAT', 'Global Wafer Inc.', 'PackagePro OSAT', 'AeroChip Test', 'PackagePro OSAT', 'AeroChip Test'], 
        'Failure_Mode': ['Wire Bond Short', 'Parametric Drift (Vt)', 'Die Crack', 'ESD Damage', 'Package Delamination', 'Wire Bond Short'],
        'Date_Reported': pd.to_datetime(['2023-09-15', '2023-09-10', '2023-08-28', '2023-08-25', '2023-08-20', '2023-09-18']), 
        'Status': ['Open', 'Analysis', 'Closed', 'Closed', 'Analysis', 'Open']
    })
    
    data['apqp_data'] = pd.DataFrame({
        'Part_Number': ['KU-ASIC-COM-002', 'KU-ASIC-RF-003', 'KU-ASIC-MEM-001', 'KU-ASIC-PWR-004'], 'Supplier': ['Global Wafer Inc.', 'AeroChip Test', 'Silicon Foundry Corp.', 'PackagePro OSAT'],
        'Stage': ['2. Product Design', '4. Validation', '5. Production', '3. Process Design'], 'Status': ['On Track', 'At Risk', 'Approved', 'On Track'],
        'Owner': ['J. Doe', 'S. Smith', 'A. Wong', 'J. Doe'], 'Start': ['2023-08-01', '2023-06-15', '2023-03-01', '2023-09-01'], 'Finish': ['2023-10-30', '2023-11-15', '2023-09-01', '2023-12-20']
    })
    
    return data

# --- ROBUST STATE INITIALIZATION ---
if 'app_data' not in st.session_state:
    st.session_state['app_data'] = generate_data()

app_data = st.session_state['app_data']
suppliers = app_data['suppliers']
foundry_perf = app_data['foundry_perf']
osat_perf = app_data['osat_perf']
failures = app_data['failures']

# --- SIDEBAR NAVIGATION AND NARRATIVE ---
st.sidebar.title("🛰️ Kuiper SQE Command Center")
st.sidebar.markdown("---")
st.sidebar.info("This application is a functional portfolio piece demonstrating the tools and analytical mindset required for the **Sr. Supplier Quality Engineer (ASIC)** role at Project Kuiper.")
st.sidebar.markdown("---")
st.sidebar.header("Workflow Modules")

# --- UI RENDER ---
st.title("Executive Summary: Global Command Center")
st.caption(f"Data Last Refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("This dashboard provides a 'single pane of glass' overview of the entire ASIC supply chain health, separating **Frontend (Foundry)** and **Backend (OSAT)** health for precise monitoring, prioritization, and risk assessment.")

st.subheader("Key Performance Indicators (Last 30 Days)")
agg_osat_30d = osat_perf[osat_perf['Date'] >= osat_perf['Date'].max() - pd.Timedelta(days=30)].groupby('Date').mean(numeric_only=True).reset_index()
agg_foundry_30d = foundry_perf[foundry_perf['Date'] >= foundry_perf['Date'].max() - pd.Timedelta(days=30)].groupby('Date').mean(numeric_only=True).reset_index()

st.markdown("##### Backend (OSAT) Health")
col1, col2, col3 = st.columns(3)
with col1:
    latest_fty = agg_osat_30d.iloc[-1]['Final_Test_Yield']
    st.metric("Avg. Final Test Yield (FTY)", f"{latest_fty:.2%}")
    st.caption("**What:** The percentage of packaged chips that pass final electrical testing. **Why:** This is a primary driver of final unit cost. A small drop in FTY at Kuiper's scale results in significant cost impact. **Standard:** Monitored as part of a **Six Sigma** program.")
with col2:
    latest_dppm = agg_osat_30d.iloc[-1]['DPPM']
    st.metric("Aggregate OSAT DPPM", f"{int(latest_dppm)}")
    st.caption("**What:** Defects Per Million shipped to Kuiper. **Why:** This is the ultimate measure of outgoing quality from our OSAT partners, directly impacting the reliability of the Kuiper constellation. **Standard:** **AS9100D Clause 8.4** (Control of External Providers).")
with col3:
    osat_issues = failures[(failures['Status'] != 'Closed') & (suppliers.loc[suppliers['Supplier'] == failures['Supplier'], 'Type'].iloc[0] == 'OSAT' if not failures.empty else False)].shape[0]
    st.metric("Active OSAT Issues", f"{osat_issues}")
    st.caption("**What:** Open SCARs/FAs related to assembly and test. **Why:** Tracks the active problem-solving workload for the backend supply chain.")

st.markdown("##### Frontend (Foundry) Health")
col4, col5, col6 = st.columns(3)
with col4:
    latest_sort_yield = agg_foundry_30d.iloc[-1]['Wafer_Sort_Yield']
    st.metric("Avg. Wafer Sort Yield", f"{latest_sort_yield:.2%}")
    st.caption("**What:** The percentage of good dies per wafer at electrical wafer sort. **Why:** The primary indicator of foundry process health and stability.")
with col5:
    latest_d0 = agg_foundry_30d.iloc[-1]['Defect_Density_D0']
    st.metric("Avg. Defect Density (D0)", f"{latest_d0:.3f}")
    st.caption("**What:** The number of random defects per square centimeter on the wafer. **Why:** A direct measure of the foundry's fab cleanliness and process control. A rising D0 is a leading indicator of future reliability problems. **Standard:** A core metric in semiconductor manufacturing physics.")
with col6:
    foundry_issues = failures[(failures['Status'] != 'Closed') & (suppliers.loc[suppliers['Supplier'] == failures['Supplier'], 'Type'].iloc[0] == 'Foundry' if not failures.empty else False)].shape[0]
    st.metric("Active Foundry Issues", f"{foundry_issues}")
    st.caption("**What:** Open SCARs/FAs related to wafer fabrication. **Why:** Tracks the problem-solving workload for the most critical part of the supply chain.")

st.divider()

st.subheader("Supplier Scorecard Matrix")
st.markdown("- **Actionability:** This integrated view allows for direct comparison. `N/A` values correctly show that certain metrics only apply to specific supplier types.")
latest_foundry = foundry_perf.loc[foundry_perf.groupby('Supplier')['Date'].idxmax()]
latest_osat = osat_perf.loc[osat_perf.groupby('Supplier')['Date'].idxmax()]
summary_df = pd.merge(suppliers, latest_foundry[['Supplier', 'Wafer_Sort_Yield', 'Defect_Density_D0']], on='Supplier', how='left')
summary_df = pd.merge(summary_df, latest_osat[['Supplier', 'Final_Test_Yield', 'DPPM']], on='Supplier', how='left')
def style_scorecard(df):
    def color_health(val):
        color = 'indianred' if val < 70 else ('orange' if val < 90 else 'mediumseagreen')
        return f'background-color: {color}; color: white'
    return df.style.map(color_health, subset=['Health_Score']).format({
        'Wafer_Sort_Yield': "{:.2%}", 'Final_Test_Yield': "{:.2%}", 'Defect_Density_D0': "{:.3f}", 'DPPM': "{:.0f}"
    }, na_rep="N/A")
st.dataframe(style_scorecard(summary_df[['Supplier', 'Type', 'Health_Score', 'Wafer_Sort_Yield', 'Defect_Density_D0', 'Final_Test_Yield', 'DPPM', 'Open_SCARs']]), use_container_width=True)
    
st.divider()
col1, col2 = st.columns((2, 1))
with col1:
    st.subheader("ML: Strategic Supplier Risk Matrix")
    st.markdown("- **Why (Actionability):** This visualization allows an SQE to instantly diagnose the *type* of risk a supplier represents and deploy the correct mitigation strategy for each quadrant.")
    summary_df['Risk_Prob'] = (100 - summary_df['Health_Score']) / 100.0 + summary_df['Open_SCARs'] * 0.15
    summary_df['Risk_Prob'] = np.clip(summary_df['Risk_Prob'], 0.05, 0.95)
    avg_health = summary_df['Health_Score'].mean(); avg_scars = summary_df['Open_SCARs'].mean()
    fig_risk_matrix = px.scatter(
        summary_df, x="Health_Score", y="Open_SCARs", size="Risk_Prob", color="Risk_Prob",
        color_continuous_scale="Reds", hover_name="Supplier", text="Supplier", size_max=60,
        title="Supplier Risk Diagnostic Matrix",
        labels={ "Health_Score": "Performance Risk (Lower Health Score = Higher Risk →)", "Open_SCARs": "Issue Risk (More SCARs = Higher Risk ↑)", "Risk_Prob": "Predicted Risk" },
        hover_data={'Health_Score': ':.1f', 'Open_SCARs': True, 'Risk_Prob': ':.0%'}
    )
    fig_risk_matrix.update_traces(textposition='top center'); fig_risk_matrix.update_xaxes(autorange="reversed")
    fig_risk_matrix.add_vline(x=avg_health, line_dash="dash", line_color="gray"); fig_risk_matrix.add_hline(y=avg_scars, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_risk_matrix, use_container_width=True, key="risk_matrix_chart")
with col2:
    st.subheader("Top ASIC Failure Modes (Pareto)")
    st.markdown("- **Actionability:** This Pareto chart applies the 80/20 rule to quality issues. Focusing on **'Wire Bond Short'** and **'Parametric Drift'** would address the majority of our current field failures, maximizing engineering impact.")
    failure_counts = failures['Failure_Mode'].value_counts().reset_index()
    fig_pareto = px.bar(failure_counts, x='count', y='Failure_Mode', orientation='h', labels={'Failure_Mode': '', 'count': 'Number of Incidents'}, text='count')
    fig_pareto.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_pareto, use_container_width=True, key="pareto_failures")
