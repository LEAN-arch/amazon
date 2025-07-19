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

# --- ATOMIC DATA INITIALIZATION FUNCTION ---
@st.cache_data
def generate_data():
    """Generates all necessary dataframes and returns them in a single dictionary."""
    data = {}
    data['suppliers'] = pd.DataFrame({
        'Supplier': ['Global Wafer Inc.', 'Quantum Assembly', 'AeroChip Test', 'Silicon Foundry Corp.', 'PackagePro OSAT'],
        'Type': ['Foundry', 'OSAT', 'OSAT', 'Foundry', 'OSAT'],
        'Location': ['Austin, TX', 'Penang, Malaysia', 'Hsinchu, Taiwan', 'Phoenix, AZ', 'Manila, Philippines'],
        'lat': [30.2672, 5.4145, 24.8138, 33.4484, 14.5995], 'lon': [-97.7431, 100.3327, 120.9676, -112.0740, 120.9842],
        'Health_Score': [92, 78, 95, 85, 65], 'Open_SCARs': [0, 1, 3, 1, 4], 'AS9100D_Cert': ['Yes', 'Yes', 'Yes', 'Yes', 'In Progress']
    })
    
    date_rng = pd.to_datetime(pd.date_range(start='2023-01-01', end='2023-09-30', freq='D'))
    performance_data = []
    for supplier in data['suppliers']['Supplier']:
        base_yield = 0.98 if 'Foundry' in supplier else 0.995; base_dppm = 20 if 'Foundry' in supplier else 75
        for date in date_rng:
            yield_val = base_yield - (np.random.rand() * 0.05) + (np.sin(date.dayofyear / 50) * 0.01)
            dppm_val = base_dppm + np.random.randint(-10, 50) + (np.sin(date.dayofyear / 30) * 20)
            performance_data.append([date, supplier, yield_val, max(0, dppm_val)])
    data['performance_data'] = pd.DataFrame(performance_data, columns=['Date', 'Supplier', 'Yield', 'DPPM'])
    data['performance_data'].loc[(data['performance_data']['Supplier'] == 'PackagePro OSAT') & (data['performance_data']['Date'] > '2023-08-15'), 'DPPM'] += 150
    
    data['failures'] = pd.DataFrame({
        'Failure_ID': ['FA-001', 'FA-002', 'FA-003', 'FA-004', 'FA-005'], 'Part_Number': ['KU-ASIC-COM-001', 'KU-ASIC-PWR-003', 'KU-ASIC-COM-001', 'KU-ASIC-RF-002', 'KU-ASIC-PWR-003'],
        'Supplier': ['PackagePro OSAT', 'Global Wafer Inc.', 'PackagePro OSAT', 'AeroChip Test', 'PackagePro OSAT'], 'Failure_Mode': ['Wire Bond Lift', 'Gate Oxide Leakage', 'Package Crack', 'ESD Damage', 'Wire Bond Lift'],
        'Date_Reported': pd.to_datetime(['2023-09-15', '2023-09-10', '2023-08-28', '2023-08-25', '2023-08-20']), 'Status': ['Open', 'Analysis', 'Closed', 'Closed', 'Analysis']
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
perf_df = app_data['performance_data']
failures = app_data['failures']

# --- SIDEBAR NAVIGATION AND NARRATIVE ---
st.sidebar.title("🛰️ Kuiper SQE Command Center")
st.sidebar.markdown("---")
st.sidebar.info(
    """
    This application is a functional portfolio piece demonstrating the tools and analytical mindset required for the **Sr. Supplier Quality Engineer (ASIC)** role at Project Kuiper.
    
    Each page represents a core SQE workflow, from high-level monitoring to deep-dive analysis and action.
    """
)
st.sidebar.markdown("---")
st.sidebar.header("Workflow Modules")

# --- UI RENDER ---
st.title("Executive Summary: Global Command Center")
st.caption(f"Data Last Refreshed: {time.strftime('%Y-%m-%d %H:%M:%S')}")
st.markdown("This dashboard provides a 'single pane of glass' overview of the entire ASIC supply chain health, enabling rapid prioritization and risk assessment.")

st.subheader("Key Performance Indicators (Last 30 Days)")
agg_perf_30d = perf_df[perf_df['Date'] >= perf_df['Date'].max() - pd.Timedelta(days=30)].groupby('Date').mean(numeric_only=True).reset_index()

def create_sparkline(data, y_axis, color):
    fig = go.Figure(go.Scatter(x=data['Date'], y=data[y_axis], mode='lines', line=dict(color=color, width=2), fill='tozeroy'))
    fig.update_layout(height=50, margin=dict(l=0, r=0, t=5, b=0), xaxis_visible=False, yaxis_visible=False)
    return fig

col1, col2, col3 = st.columns(3)
with col1:
    avg_health = int(suppliers['Health_Score'].mean())
    st.metric("Avg. Supplier Health", f"{avg_health}/100")
    st.caption("A weighted score of Quality, Delivery, and Responsiveness.")
with col2:
    active_issues = failures[failures['Status'] != 'Closed'].shape[0]
    st.metric("Active High-Priority Issues", f"{active_issues}")
    st.caption("A live count of open SCARs and Failure Analyses.")
with col3:
    latest_dppm = agg_perf_30d.iloc[-1]['DPPM']
    st.metric("Aggregate DPPM (Daily)", f"{int(latest_dppm)}")
    st.plotly_chart(create_sparkline(agg_perf_30d, 'DPPM', 'red'), use_container_width=True, key="spark_dppm")
    st.caption("Defects Per Million across all OSATs.")

st.divider()

st.subheader("Aggregate DPPM Trend (Last 30 Days)")
st.markdown("""
- **What:** A detailed view of the aggregated Defects Per Million (DPPM) for all OSAT suppliers over the past 30 days.
- **How:** The red line represents the daily DPPM, which can be noisy. The **blue line is a 7-day moving average**, which smooths out the daily fluctuations to reveal the true underlying trend.
- **Why (Actionability):** This chart is critical for understanding the overall health of the manufacturing backend. A sustained upward trend in the moving average, even with daily dips, is a strong signal of systemic quality degradation that requires investigation at a portfolio level.
""")
agg_perf_30d['DPPM_MA'] = agg_perf_30d['DPPM'].rolling(window=7).mean()

fig_dppm_detailed = go.Figure()
fig_dppm_detailed.add_trace(go.Scatter(x=agg_perf_30d['Date'], y=agg_perf_30d['DPPM'], mode='lines', name='Daily DPPM', line=dict(color='lightcoral')))
fig_dppm_detailed.add_trace(go.Scatter(x=agg_perf_30d['Date'], y=agg_perf_30d['DPPM_MA'], mode='lines', name='7-Day Moving Avg', line=dict(color='navy', width=3)))
fig_dppm_detailed.update_layout(
    xaxis_title="Date",
    yaxis_title="Defects Per Million (DPPM)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_dppm_detailed, use_container_width=True, key="dppm_detailed_chart")

st.divider()

col1, col2 = st.columns((2, 1))
with col1:
    st.subheader("Supplier Scorecard Matrix")
    st.markdown("- **Actionability:** Prioritize attention on suppliers with red cells. `PackagePro OSAT` requires immediate investigation.")
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
    
    st.subheader("ML: Strategic Supplier Risk Matrix")
    st.markdown("""
    - **What:** A bubble chart that plots suppliers based on their current performance (`Health_Score`) vs. their current issue load (`Open_SCARs`). The bubble's color and size represent the final ML-predicted risk probability.
    - **How:** The chart is divided into four strategic quadrants based on the average of each axis.
    - **Why (Actionability):** This visualization provides a much deeper insight than a simple ranked list. It allows an SQE to instantly diagnose the *type* of risk a supplier represents and deploy the correct mitigation strategy for each quadrant, as explained below the chart.
    """)
    
    summary_df['Risk_Prob'] = (100 - summary_df['Health_Score']) / 100.0 + summary_df['Open_SCARs'] * 0.15
    summary_df['Risk_Prob'] = np.clip(summary_df['Risk_Prob'], 0.05, 0.95)

    avg_health = summary_df['Health_Score'].mean()
    avg_scars = summary_df['Open_SCARs'].mean()

    fig_risk_matrix = px.scatter(
        summary_df, x="Health_Score", y="Open_SCARs", size="Risk_Prob", color="Risk_Prob",
        color_continuous_scale="Reds", hover_name="Supplier", text="Supplier", size_max=60,
        title="Supplier Risk Diagnostic Matrix",
        labels={ "Health_Score": "Performance Risk (Lower Health Score = Higher Risk →)", "Open_SCARs": "Issue Risk (More SCARs = Higher Risk ↑)", "Risk_Prob": "Predicted Risk" },
        hover_data={'Health_Score': ':.1f', 'Open_SCARs': True, 'Risk_Prob': ':.0%'}
    )
    fig_risk_matrix.update_traces(textposition='top center')
    fig_risk_matrix.update_xaxes(autorange="reversed")
    fig_risk_matrix.add_vline(x=avg_health, line_dash="dash", line_color="gray")
    fig_risk_matrix.add_hline(y=avg_scars, line_dash="dash", line_color="gray")
    st.plotly_chart(fig_risk_matrix, use_container_width=True, key="risk_matrix_chart")

    st.subheader("How to Act on This Matrix (Actionability Guide)")
    c1, c2 = st.columns(2)
    with c1:
        st.warning("🔴 **Top-Right: Chronic Problems**")
        st.caption("(`PackagePro OSAT`, `AeroChip Test`)\n- **Diagnosis:** Low performance AND a high number of open issues. These are our most troubled suppliers.\n- **Action:** Immediate, deep-dive intervention. Executive-level business reviews and potentially initiating a 2nd source qualification.")
        st.success("🟢 **Bottom-Left: Stable & Healthy**")
        st.caption("(`Global Wafer Inc.`)\n- **Diagnosis:** High performance and few open issues. These are our top partners.\n- **Action:** Maintain strong relationship, monitor, and leverage for new projects. Less intensive management required.")
    with c2:
        st.warning("🟠 **Top-Left: Process Instability**")
        st.caption("*(No suppliers currently in this quadrant)*\n- **Diagnosis:** Good historical performers who are currently struggling with specific, documented problems.\n- **Action:** Focus on driving SCARs to closure. Provide technical support to resolve issues quickly before performance degrades further.")
        st.warning("🟡 **Bottom-Right: Silent Decline**")
        st.caption("(`Quantum Assembly`, `Silicon Foundry Corp.`)\n- **Diagnosis:** Performance is degrading, but there are few formal, documented issues. This is a subtle but dangerous category.\n- **Action:** Proactive investigation. Perform a process audit or deep dive into their SPC data to find the undiagnosed root cause of the performance slip.")

with col2:
    st.subheader("Supplier Health Distribution")
    st.markdown("- **Actionability:** Provides a high-level portfolio view. A large 'Critical' slice indicates systemic supply chain risk.")
    def get_status(score):
        if score < 70: return 'Critical';
        if score < 90: return 'Warning';
        return 'Healthy'
    suppliers['Status'] = suppliers['Health_Score'].apply(get_status)
    status_counts = suppliers['Status'].value_counts()
    fig_donut = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values, hole=.6, marker_colors=['mediumseagreen', 'orange', 'indianred'])])
    fig_donut.update_layout(title_text='Health Status', showlegend=True, height=250, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_donut, use_container_width=True, key="donut_health")

    st.subheader("Top Failure Modes (Pareto Chart)")
    st.markdown("- **Actionability:** Applies the Pareto Principle (80/20 rule). Focusing improvement efforts on the top 1-2 failure modes will yield the largest quality impact.")
    failure_counts = failures['Failure_Mode'].value_counts().reset_index()
    fig_pareto = px.bar(failure_counts.head(5), x='count', y='Failure_Mode', orientation='h', labels={'Failure_Mode': '', 'count': 'Number of Incidents'}, text='count')
    fig_pareto.update_layout(yaxis={'categoryorder':'total ascending'}, height=300, margin=dict(t=20, b=10))
    st.plotly_chart(fig_pareto, use_container_width=True, key="pareto_failures")
