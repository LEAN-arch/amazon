import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Kuiper SQE Command Center",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MOCK DATA GENERATION (CACHE TO PREVENT RE-RUNNING) ---
@st.cache_data
def generate_data():
    # Supplier Data
    suppliers = pd.DataFrame({
        'Supplier': ['Global Wafer Inc.', 'Quantum Assembly', 'AeroChip Test', 'Silicon Foundry Corp.', 'PackagePro OSAT'],
        'Type': ['Foundry', 'OSAT', 'OSAT', 'Foundry', 'OSAT'],
        'Location': ['Austin, TX', 'Penang, Malaysia', 'Hsinchu, Taiwan', 'Phoenix, AZ', 'Manila, Philippines'],
        'lat': [30.2672, 5.4145, 24.8138, 33.4484, 14.5995],
        'lon': [-97.7431, 100.3327, 120.9676, -112.0740, 120.9842],
        'Health_Score': [92, 78, 95, 85, 65],
        'AS9100D_Cert': ['Yes', 'Yes', 'Yes', 'Yes', 'In Progress']
    })

    # Performance Data (Time Series)
    date_rng = pd.to_datetime(pd.date_range(start='2023-01-01', end='2023-09-30', freq='D'))
    performance_data = []
    for supplier in suppliers['Supplier']:
        base_yield = 0.98 if 'Foundry' in supplier else 0.995
        base_dppm = 20 if 'Foundry' in supplier else 75
        for date in date_rng:
            yield_val = base_yield - (np.random.rand() * 0.05)
            dppm_val = base_dppm + np.random.randint(-10, 50)
            performance_data.append([date, supplier, yield_val, max(0, dppm_val)])
    
    perf_df = pd.DataFrame(performance_data, columns=['Date', 'Supplier', 'Yield', 'DPPM'])
    # Simulate a process excursion for one supplier
    perf_df.loc[(perf_df['Supplier'] == 'PackagePro OSAT') & (perf_df['Date'] > '2023-08-15'), 'DPPM'] += 150

    # Failure Analysis Data
    failures = pd.DataFrame({
        'Failure_ID': ['FA-001', 'FA-002', 'FA-003', 'FA-004', 'FA-005'],
        'Part_Number': ['KU-ASIC-COM-001', 'KU-ASIC-PWR-003', 'KU-ASIC-COM-001', 'KU-ASIC-RF-002', 'KU-ASIC-PWR-003'],
        'Supplier': ['PackagePro OSAT', 'Global Wafer Inc.', 'PackagePro OSAT', 'AeroChip Test', 'PackagePro OSAT'],
        'Failure_Mode': ['Wire Bond Lift', 'Gate Oxide Leakage', 'Package Crack', 'ESD Damage', 'Wire Bond Lift'],
        'Date_Reported': pd.to_datetime(['2023-09-15', '2023-09-10', '2023-08-28', '2023-08-25', '2023-08-20']),
        'Status': ['Open', 'Analysis', 'Closed', 'Closed', 'Analysis']
    })

    # APQP/PPAP Data
    apqp_data = pd.DataFrame({
        'Part_Number': ['KU-ASIC-COM-002', 'KU-ASIC-RF-003', 'KU-ASIC-MEM-001', 'KU-ASIC-PWR-004'],
        'Stage': ['2. Product Design', '4. Validation', '5. Production', '3. Process Design'],
        'Status': ['On Track', 'At Risk', 'Approved', 'On Track'],
        'Owner': ['J. Doe', 'S. Smith', 'A. Wong', 'J. Doe']
    })
    
    # Store in session state for access across pages
    st.session_state['suppliers'] = suppliers
    st.session_state['performance_data'] = perf_df
    st.session_state['failures'] = failures
    st.session_state['apqp_data'] = apqp_data
    st.session_state['data_loaded'] = True
    return True

# Ensure data is generated once and stored in session state
if 'data_loaded' not in st.session_state:
    generate_data()

# Load data from session state
suppliers = st.session_state['suppliers']
perf_df = st.session_state['performance_data']
failures = st.session_state['failures']

st.title("🛰️ Global Command Center")
st.markdown("High-level health summary of the entire Kuiper ASIC supply chain.")

# --- KPIs ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Overall Supplier Health", f"{int(suppliers['Health_Score'].mean())}/100", delta="-2 pts vs last month", delta_color="inverse")
with col2:
    active_issues = failures[failures['Status'] != 'Closed'].shape[0]
    st.metric("Active High-Priority Issues", f"{active_issues}", "SCARs & FA")
with col3:
    avg_yield = perf_df[perf_df['Date'] == perf_df['Date'].max()]['Yield'].mean() * 100
    st.metric("Aggregate Yield (Daily)", f"{avg_yield:.2f}%")
with col4:
    avg_dppm = perf_df[perf_df['Date'] == perf_df['Date'].max()]['DPPM'].mean()
    st.metric("Aggregate DPPM (Daily)", f"{int(avg_dppm)}")

st.divider()

# --- MAIN VISUALIZATIONS ---
col1, col2 = st.columns((2, 1.5))

with col1:
    st.subheader("Supplier Scorecard Matrix")
    
    # Create a summary df for the scorecard
    summary_df = suppliers.copy()
    latest_perf = perf_df.loc[perf_df.groupby('Supplier')['Date'].idxmax()]
    summary_df = pd.merge(summary_df, latest_perf[['Supplier', 'Yield', 'DPPM']], on='Supplier')
    
    def style_scorecard(df):
        def color_health(val):
            color = 'red' if val < 70 else ('orange' if val < 90 else 'green')
            return f'background-color: {color}; color: white'
        def color_dppm(val):
            color = 'green' if val < 100 else ('orange' if val < 200 else 'red')
            return f'background-color: {color}; color: white'
        
        styled_df = df.style.map(color_health, subset=['Health_Score'])
        styled_df = styled_df.map(color_dppm, subset=['DPPM'])
        styled_df = styled_df.format({'Yield': "{:.2%}"})
        return styled_df

    st.dataframe(style_scorecard(summary_df[['Supplier', 'Type', 'Health_Score', 'Yield', 'DPPM', 'AS9100D_Cert']]), use_container_width=True)

    st.subheader("Interactive Supplier Map")
    st.map(suppliers[['lat', 'lon']], zoom=1)

with col2:
    st.subheader("Top 5 Failure Modes (Last 90 Days)")
    
    failure_counts = failures['Failure_Mode'].value_counts().reset_index()
    failure_counts.columns = ['Failure_Mode', 'Count']
    
    fig = px.bar(failure_counts.head(5), 
                 x='Count', 
                 y='Failure_Mode', 
                 orientation='h',
                 title="Failure Incidents by Type",
                 labels={'Failure_Mode': 'Failure Mode', 'Count': 'Number of Incidents'},
                 text='Count')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Live Alert Feed")
    st.warning("IQC Alert: Lot #KUI-7891 from 'PackagePro OSAT' failed visual inspection for package cracks.", icon="⚠️")
    st.info("SPC Monitor: 'Global Wafer Inc.' Photolithography CD shows minor upward trend.", icon="📈")
    st.error("STOP SHIP: Active failure analysis FA-001 for 'PackagePro OSAT' on part KU-ASIC-COM-001.", icon="🛑")

st.sidebar.success("Select a module above to continue.")
