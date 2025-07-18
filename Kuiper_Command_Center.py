import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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
        'Open_SCARs': [0, 1, 0, 1, 3],
        'AS9100D_Cert': ['Yes', 'Yes', 'Yes', 'Yes', 'In Progress']
    })

    # Performance Data (Time Series)
    date_rng = pd.to_datetime(pd.date_range(start='2023-01-01', end='2023-09-30', freq='D'))
    performance_data = []
    for supplier in suppliers['Supplier']:
        base_yield = 0.98 if 'Foundry' in supplier else 0.995
        base_dppm = 20 if 'Foundry' in supplier else 75
        for date in date_rng:
            yield_val = base_yield - (np.random.rand() * 0.05) + (np.sin(date.dayofyear / 50) * 0.01)
            dppm_val = base_dppm + np.random.randint(-10, 50) + (np.sin(date.dayofyear / 30) * 20)
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
        'Supplier': ['Global Wafer Inc.', 'AeroChip Test', 'Silicon Foundry Corp.', 'PackagePro OSAT'],
        'Stage': ['2. Product Design', '4. Validation', '5. Production', '3. Process Design'],
        'Status': ['On Track', 'At Risk', 'Approved', 'On Track'],
        'Owner': ['J. Doe', 'S. Smith', 'A. Wong', 'J. Doe'],
        'Start': ['2023-08-01', '2023-06-15', '2023-03-01', '2023-09-01'],
        'Finish': ['2023-10-30', '2023-11-15', '2023-09-01', '2023-12-20']
    })
    
    st.session_state.update({
        'suppliers': suppliers, 'performance_data': perf_df,
        'failures': failures, 'apqp_data': apqp_data, 'data_loaded': True
    })
    return True

if 'data_loaded' not in st.session_state:
    generate_data()

suppliers = st.session_state['suppliers']
perf_df = st.session_state['performance_data']
failures = st.session_state['failures']

st.title("🛰️ Global Command Center")
st.markdown("High-level health summary of the entire Kuiper ASIC supply chain, augmented with predictive analytics.")

# --- KPIs with Contextual Plots ---
st.subheader("Key Performance Indicators (Last 30 Days)")

# THIS IS THE CORRECTED LINE
agg_perf_30d = perf_df[perf_df['Date'] >= perf_df['Date'].max() - pd.Timedelta(days=30)].groupby('Date').mean(numeric_only=True).reset_index()


def create_sparkline(data, y_axis, color):
    fig = go.Figure(go.Scatter(x=data['Date'], y=data[y_axis], mode='lines', line=dict(color=color, width=2), fill='tozeroy'))
    fig.update_layout(height=50, margin=dict(l=0, r=0, t=5, b=0), xaxis_visible=False, yaxis_visible=False)
    return fig

col1, col2, col3 = st.columns(3)
with col1:
    avg_health = int(suppliers['Health_Score'].mean())
    st.metric("Avg. Supplier Health", f"{avg_health}/100", f"{avg_health-82} vs Q2 Avg", delta_color="normal")
    st.caption("Weighted score of Quality, Delivery, and Responsiveness.")
with col2:
    active_issues = failures[failures['Status'] != 'Closed'].shape[0]
    st.metric("Active High-Priority Issues", f"{active_issues}", f"{active_issues - 1} vs last week", delta_color="inverse")
    st.caption("Open SCARs and Failure Analyses requiring immediate attention.")
with col3:
    latest_dppm = agg_perf_30d.iloc[-1]['DPPM']
    st.metric("Aggregate DPPM (Daily)", f"{int(latest_dppm)}", f"{int(latest_dppm - agg_perf_30d.iloc[-2]['DPPM'])} vs yesterday", delta_color="inverse")
    st.plotly_chart(create_sparkline(agg_perf_30d, 'DPPM', 'red'), use_container_width=True)
    st.caption("Defects Per Million across all OSATs. Lower is better.")

st.divider()

# --- MAIN VISUALIZATIONS ---
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("Supplier Scorecard Matrix")
    st.caption("Live ranking of all suppliers. Click column headers to sort. Red/Orange/Green colors indicate performance against targets.")
    summary_df = suppliers.copy()
    latest_perf = perf_df.loc[perf_df.groupby('Supplier')['Date'].idxmax()]
    summary_df = pd.merge(summary_df, latest_perf[['Supplier', 'Yield', 'DPPM']], on='Supplier')
    
    def style_scorecard(df):
        def color_health(val):
            color = 'indianred' if val < 70 else ('orange' if val < 90 else 'mediumseagreen')
            return f'background-color: {color}; color: white'
        def color_dppm(val):
            color = 'mediumseagreen' if val < 100 else ('orange' if val < 200 else 'indianred')
            return f'background-color: {color}; color: white'
        
        return df.style.map(color_health, subset=['Health_Score']).map(color_dppm, subset=['DPPM']).format({'Yield': "{:.2%}"})

    st.dataframe(style_scorecard(summary_df[['Supplier', 'Type', 'Health_Score', 'Yield', 'DPPM', 'Open_SCARs']]), use_container_width=True)
    
    st.subheader("ML: Supplier Risk Forecast (Next Quarter)")
    st.info("A simple classification model predicts the likelihood of a supplier's Health Score dropping into the 'At Risk' category (<80) next quarter based on recent performance trends and open issues.", icon="🤖")
    
    # Simulate ML model prediction
    summary_df['Risk_Prob'] = (100 - summary_df['Health_Score']) / 100.0 + summary_df['Open_SCARs'] * 0.1
    summary_df['Risk_Prob'] = np.clip(summary_df['Risk_Prob'], 0.05, 0.95)
    
    fig_risk = px.bar(summary_df.sort_values('Risk_Prob', ascending=True), 
                      x='Risk_Prob', y='Supplier', orientation='h', 
                      title="Predicted Probability of Becoming 'At Risk'",
                      labels={'Risk_Prob': 'Probability', 'Supplier': ''},
                      text=summary_df['Risk_Prob'].apply(lambda x: f'{x:.0%}'))
    fig_risk.update_traces(marker_color=summary_df['Risk_Prob'], marker_colorscale='Reds')
    st.plotly_chart(fig_risk, use_container_width=True)

with col2:
    st.subheader("Supplier Health Distribution")
    st.caption("Current breakdown of suppliers by health status.")
    
    def get_status(score):
        if score < 70: return 'Critical'
        if score < 90: return 'Warning'
        return 'Healthy'
    suppliers['Status'] = suppliers['Health_Score'].apply(get_status)
    status_counts = suppliers['Status'].value_counts()
    
    fig_donut = go.Figure(data=[go.Pie(labels=status_counts.index, 
                                       values=status_counts.values, 
                                       hole=.6,
                                       marker_colors=['mediumseagreen', 'orange', 'indianred'])])
    fig_donut.update_layout(title_text='Health Status', showlegend=True, height=250, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_donut, use_container_width=True)

    st.subheader("Top Failure Modes (Last 90 Days)")
    failure_counts = failures['Failure_Mode'].value_counts().reset_index()
    fig_pareto = px.bar(failure_counts.head(5), 
                        x='count', y='Failure_Mode', orientation='h',
                        labels={'Failure_Mode': '', 'count': 'Number of Incidents'}, text='count')
    fig_pareto.update_layout(yaxis={'categoryorder':'total ascending'}, height=300, margin=dict(t=20, b=10))
    st.plotly_chart(fig_pareto, use_container_width=True)

st.sidebar.success("Select a module above to continue.")
