import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

st.set_page_config(layout="wide", page_title="Supplier Deep Dive", page_icon="🔬")

if 'data_loaded' not in st.session_state:
    st.error("Data not loaded. Please go to the main page first.")
    st.stop()

suppliers = st.session_state['suppliers']
perf_df = st.session_state['performance_data']

st.markdown("# 🔬 Supplier Deep Dive")
st.markdown("Analyze individual supplier performance, review process control data, and leverage ML for predictive quality.")

selected_supplier = st.selectbox("Select a Supplier to Analyze", suppliers['Supplier'].unique())
supplier_data = perf_df[perf_df['Supplier'] == selected_supplier].copy()
supplier_info = suppliers[suppliers['Supplier'] == selected_supplier].iloc[0]

# --- TABS FOR DIFFERENT ANALYSIS VIEWS ---
tab1, tab2, tab3 = st.tabs(["Performance Trends", "Process Control & SPC", "🤖 ML: Predictive Lot Disposition"])

with tab1:
    st.subheader(f"Performance Trends for: {selected_supplier}")
    supplier_data['Yield_MA'] = supplier_data['Yield'].rolling(window=14).mean()
    supplier_data['DPPM_MA'] = supplier_data['DPPM'].rolling(window=14).mean()

    col1, col2 = st.columns(2)
    with col1:
        fig_yield = go.Figure()
        fig_yield.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['Yield'], mode='lines', name='Daily Yield', line=dict(color='lightblue')))
        fig_yield.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['Yield_MA'], mode='lines', name='14-Day Moving Avg', line=dict(color='blue', width=3)))
        fig_yield.update_layout(title="Yield Trend with Moving Average", yaxis_title="Yield (%)", yaxis_tickformat=".2%")
        st.plotly_chart(fig_yield, use_container_width=True)
        st.caption("The moving average helps identify underlying trends by smoothing out daily noise.")

    with col2:
        fig_dppm = go.Figure()
        fig_dppm.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['DPPM'], mode='lines', name='Daily DPPM', line=dict(color='lightcoral')))
        fig_dppm.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['DPPM_MA'], mode='lines', name='14-Day Moving Avg', line=dict(color='red', width=3)))
        fig_dppm.update_layout(title="DPPM Trend with Moving Average", yaxis_title="Defects Per Million (DPPM)")
        st.plotly_chart(fig_dppm, use_container_width=True)
        st.caption("A rising DPPM trend is a key indicator of degrading quality and requires investigation.")

with tab2:
    st.subheader("Statistical Process Control (SPC) Chart")
    st.caption("Simulated data for a critical process parameter (e.g., Gate Oxide Thickness). This chart helps detect process drift *before* it results in defects.")
    
    np.random.seed(42)
    target, ucl, lcl = 10.0, 10.5, 9.5
    spc_data = np.random.normal(loc=target, scale=0.15, size=50)
    spc_data[30:35] += 0.6  # Excursion
    ooc_points = [i for i, val in enumerate(spc_data) if val > ucl or val < lcl]

    fig_spc = go.Figure()
    fig_spc.add_trace(go.Scatter(y=spc_data, mode='lines+markers', name='Measurement'))
    fig_spc.add_hline(y=target, line=dict(dash="dash", color="green"), name="Target")
    fig_spc.add_hline(y=ucl, line=dict(dash="dot", color="red"), name="UCL")
    fig_spc.add_hline(y=lcl, line=dict(dash="dot", color="red"), name="LCL")
    fig_spc.add_trace(go.Scatter(x=ooc_points, y=spc_data[ooc_points], mode='markers', marker=dict(color='red', size=10, symbol='x'), name='Out of Control'))
    fig_spc.update_layout(title="SPC Chart for Critical Parameter", yaxis_title="Measurement (nm)", xaxis_title="Batch Number")
    st.plotly_chart(fig_spc, use_container_width=True)

with tab3:
    st.subheader("Predictive Lot Disposition Engine")
    st.info("This ML model predicts the probability of a lot failing final test based on upstream process parameters. This allows for targeted, risk-based inspection rather than random sampling.", icon="🤖")

    # --- SIMULATE TRAINING DATA AND A MODEL ---
    @st.cache_data
    def get_model_and_data():
        np.random.seed(42)
        X = pd.DataFrame({
            'Temp_Avg': np.random.normal(150, 5, 200),
            'Pressure_Var': np.random.gamma(1, 0.5, 200),
            'Vibration_Max': np.random.uniform(0.1, 1.0, 200)
        })
        # Create a relationship for failure
        y = ((X['Temp_Avg'] > 155) | (X['Pressure_Var'] > 1.2) | (X['Vibration_Max'] > 0.8)).astype(int)
        y = y & (np.random.rand(200) < 0.7) # Add some noise
        
        # Train a simple model
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        return model, X.describe()

    model, X_desc = get_model_and_data()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("##### Input New Lot Parameters:")
        temp = st.slider("Average Temp (°C)", float(X_desc.loc['min','Temp_Avg']), float(X_desc.loc['max','Temp_Avg']), 152.0, 0.1)
        pressure = st.slider("Pressure Variance (psi)", float(X_desc.loc['min','Pressure_Var']), float(X_desc.loc['max','Pressure_Var']), 0.8, 0.01)
        vibration = st.slider("Max Vibration (g)", float(X_desc.loc['min','Vibration_Max']), float(X_desc.loc['max','Vibration_Max']), 0.5, 0.01)
        
        # Predict
        input_data = pd.DataFrame([[temp, pressure, vibration]], columns=['Temp_Avg', 'Pressure_Var', 'Vibration_Max'])
        fail_prob = model.predict_proba(input_data)[0, 1]

    with col2:
        st.markdown("##### Model Prediction & Recommendation:")
        if fail_prob > 0.6:
            st.error(f"**High Risk ({fail_prob:.0%})** - Recommend placing lot on hold for engineering review.", icon="🚨")
        elif fail_prob > 0.3:
            st.warning(f"**Medium Risk ({fail_prob:.0%})** - Recommend enhanced inspection (100% AQL).", icon="⚠️")
        else:
            st.success(f"**Low Risk ({fail_prob:.0%})** - Recommend standard release protocol.", icon="✅")

        st.progress(fail_prob)

        st.markdown("##### What's Driving This Prediction?")
        st.caption("Feature importance shows which parameters the model considers most predictive of failure. This helps focus engineering efforts.")
        
        importances = model.feature_importances_
        feature_names = input_data.columns
        fig_imp = px.bar(x=importances, y=feature_names, orientation='h', labels={'x':'Importance', 'y':''}, title="Model Feature Importance")
        st.plotly_chart(fig_imp, use_container_width=True)
