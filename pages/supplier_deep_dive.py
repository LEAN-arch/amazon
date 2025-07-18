import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
from prophet import Prophet
from pptx import Presentation
from pptx.util import Inches
import io

st.set_page_config(layout="wide", page_title="Supplier Deep Dive", page_icon="🔬")

# --- ROBUST STATE CHECK ---
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please go to the 'Global Command Center' home page to initialize the app.")
    st.stop()

# Unpack data from the session state dictionary
app_data = st.session_state['app_data']
suppliers = app_data['suppliers']
perf_df = app_data['performance_data']
failures = app_data['failures']

# --- UI RENDER ---
st.markdown("# 🔬 Supplier Deep Dive")
st.markdown("Analyze individual supplier performance, review process control data, and leverage ML for predictive quality.")

selected_supplier = st.selectbox("Select a Supplier to Analyze", suppliers['Supplier'].unique(), key="supplier_select_deep_dive")
supplier_data = perf_df[perf_df['Supplier'] == selected_supplier].copy()
supplier_info = suppliers[suppliers['Supplier'] == selected_supplier].iloc[0]

tab_perf, tab_forecast, tab_ml, tab_report = st.tabs(["Performance & SPC", "📈 Forecasting (Prophet)", "🤖 Predictive Disposition", "📋 Automated Reporting"])

with tab_perf:
    st.header(f"Historical Performance for: {selected_supplier}")
    supplier_data['Yield_MA'] = supplier_data['Yield'].rolling(window=14).mean()
    supplier_data['DPPM_MA'] = supplier_data['DPPM'].rolling(window=14).mean()

    col1, col2 = st.columns(2)
    with col1:
        fig_yield = go.Figure()
        fig_yield.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['Yield'], mode='lines', name='Daily Yield', line=dict(color='lightblue')))
        fig_yield.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['Yield_MA'], mode='lines', name='14-Day Moving Avg', line=dict(color='blue', width=3)))
        fig_yield.update_layout(title="Yield Trend with Moving Average", yaxis_title="Yield (%)", yaxis_tickformat=".2%")
        st.plotly_chart(fig_yield, use_container_width=True, key="yield_chart")
    with col2:
        fig_dppm = go.Figure()
        fig_dppm.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['DPPM'], mode='lines', name='Daily DPPM', line=dict(color='lightcoral')))
        fig_dppm.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['DPPM_MA'], mode='lines', name='14-Day Moving Avg', line=dict(color='red', width=3)))
        fig_dppm.update_layout(title="DPPM Trend with Moving Average", yaxis_title="Defects Per Million (DPPM)")
        st.plotly_chart(fig_dppm, use_container_width=True, key="dppm_chart")

    st.subheader("Statistical Process Control (SPC) Chart")
    st.caption("Simulated data for a critical process parameter.")
    np.random.seed(42)
    target, ucl, lcl = 10.0, 10.5, 9.5
    spc_data = np.random.normal(loc=target, scale=0.15, size=50)
    spc_data[30:35] += 0.6  # Excursion
    fig_spc = go.Figure()
    fig_spc.add_trace(go.Scatter(y=spc_data, mode='lines+markers', name='Measurement'))
    fig_spc.add_hline(y=target, line=dict(dash="dash", color="green"), name="Target")
    fig_spc.add_hline(y=ucl, line=dict(dash="dot", color="red"), name="UCL")
    fig_spc.add_hline(y=lcl, line=dict(dash="dot", color="red"), name="LCL")
    fig_spc.update_layout(title="SPC Chart for Critical Parameter", yaxis_title="Measurement (nm)", xaxis_title="Batch Number")
    st.plotly_chart(fig_spc, use_container_width=True, key="spc_chart")

with tab_forecast:
    st.header("Predictive Quality Forecasting using Prophet")
    st.info("This module uses Meta's Prophet library to forecast key quality metrics 30 days into the future. It helps identify potential issues *before* they occur.", icon="🔮")

    @st.cache_data
    def run_prophet_forecast(data, metric_col, periods=30):
        prophet_df = data[['Date', metric_col]].rename(columns={'Date': 'ds', metric_col: 'y'})
        m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
        m.fit(prophet_df)
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        return m, forecast

    metric_to_forecast = st.selectbox("Select metric to forecast:", ["DPPM", "Yield"], key="forecast_metric_select")
    
    with st.spinner(f"Generating 30-day forecast for {metric_to_forecast}..."):
        model, forecast = run_prophet_forecast(supplier_data, metric_to_forecast)
        st.subheader("Forecast Plot")
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast (yhat)', line=dict(color='navy', dash='dash')))
        fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='rgba(0,176,246,0.2)', name='Upper Bound'))
        fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(0,176,246,0.2)', name='Lower Bound'))
        fig_forecast.add_trace(go.Scatter(x=model.history['ds'], y=model.history['y'], mode='markers', name='Actuals', marker=dict(color='black', size=4)))
        fig_forecast.update_layout(title=f"Forecast of {metric_to_forecast} for {selected_supplier}", yaxis_title=metric_to_forecast)
        st.plotly_chart(fig_forecast, use_container_width=True, key="prophet_forecast_chart")
        
        st.subheader("Actionable Insights from Forecast")
        if metric_to_forecast == 'DPPM':
            threshold = 150
            future_dppm = forecast[forecast['ds'] > pd.Timestamp.now()]
            if not future_dppm.empty and (future_dppm['yhat'] > threshold).any():
                breach_date = future_dppm[future_dppm['yhat'] > threshold]['ds'].iloc[0]
                st.error(f"**ALERT:** DPPM is forecast to exceed the {threshold}ppm threshold on **{breach_date.strftime('%Y-%m-%d')}**. Recommend proactive engagement with supplier.", icon="🚨")
            else:
                st.success(f"**OK:** DPPM is forecast to remain below the {threshold}ppm threshold for the next 30 days.", icon="✅")
        
        st.subheader("Forecast Components")
        st.caption("Prophet deconstructs the forecast into its underlying components: overall trend, weekly, and yearly patterns.")
        fig_components = model.plot_components(forecast)
        
        # THIS IS THE CORRECTED LINE: The 'key' argument has been removed.
        st.pyplot(fig_components)

with tab_ml:
    st.header("Predictive Lot Disposition Engine")
    st.info("This ML model predicts the probability of a lot failing final test based on upstream process parameters.", icon="🤖")

    @st.cache_data
    def get_model_and_data():
        np.random.seed(42)
        X = pd.DataFrame({'Temp_Avg': np.random.normal(150, 5, 200), 'Pressure_Var': np.random.gamma(1, 0.5, 200), 'Vibration_Max': np.random.uniform(0.1, 1.0, 200)})
        y = ((X['Temp_Avg'] > 155) | (X['Pressure_Var'] > 1.2) | (X['Vibration_Max'] > 0.8)).astype(int)
        y = y & (np.random.rand(200) < 0.7)
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        model.fit(X, y)
        return model, X.describe()

    model, X_desc = get_model_and_data()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("##### Input New Lot Parameters:")
        temp = st.slider("Average Temp (°C)", float(X_desc.loc['min','Temp_Avg']), float(X_desc.loc['max','Temp_Avg']), 152.0, 0.1, key="slider_temp")
        pressure = st.slider("Pressure Variance (psi)", float(X_desc.loc['min','Pressure_Var']), float(X_desc.loc['max','Pressure_Var']), 0.8, 0.01, key="slider_pressure")
        vibration = st.slider("Max Vibration (g)", float(X_desc.loc['min','Vibration_Max']), float(X_desc.loc['max','Vibration_Max']), 0.5, 0.01, key="slider_vibration")
        input_data = pd.DataFrame([[temp, pressure, vibration]], columns=['Temp_Avg', 'Pressure_Var', 'Vibration_Max'])
        fail_prob = model.predict_proba(input_data)[0, 1]
    with col2:
        st.markdown("##### Model Prediction & Recommendation:")
        if fail_prob > 0.6: st.error(f"**High Risk ({fail_prob:.0%})** - Recommend placing lot on hold for engineering review.", icon="🚨")
        elif fail_prob > 0.3: st.warning(f"**Medium Risk ({fail_prob:.0%})** - Recommend enhanced inspection (100% AQL).", icon="⚠️")
        else: st.success(f"**Low Risk ({fail_prob:.0%})** - Recommend standard release protocol.", icon="✅")
        st.progress(fail_prob)
        st.markdown("##### What's Driving This Prediction?")
        importances = model.feature_importances_
        feature_names = input_data.columns
        fig_imp = px.bar(x=importances, y=feature_names, orientation='h', labels={'x':'Importance', 'y':''}, title="Model Feature Importance")
        st.plotly_chart(fig_imp, use_container_width=True, key="importance_chart")

with tab_report:
    st.header("Automated Supplier Quality Report")
    st.info("Generate a standardized PowerPoint (PPTX) report for this supplier, including key metrics and performance charts.", icon="📄")

    if st.button("Generate PowerPoint Report"):
        with st.spinner("Creating report... This may take a moment."):
            prs = Presentation()
            title_slide_layout = prs.slide_layouts[0]
            slide = prs.slides.add_slide(title_slide_layout)
            title = slide.shapes.title
            subtitle = slide.placeholders[1]
            title.text = f"Supplier Quality Review: {selected_supplier}"
            subtitle.text = f"Report Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d')}"

            content_slide_layout = prs.slide_layouts[5]
            slide = prs.slides.add_slide(content_slide_layout)
            slide.shapes.title.text = "Key Performance Trends"
            
            yield_img_bytes = fig_yield.to_image(format="png", engine="kaleido", width=800, height=400)
            slide.shapes.add_picture(io.BytesIO(yield_img_bytes), Inches(0.5), Inches(1.5), width=Inches(4.5))
            
            dppm_img_bytes = fig_dppm.to_image(format="png", engine="kaleido", width=800, height=400)
            slide.shapes.add_picture(io.BytesIO(dppm_img_bytes), Inches(5.0), Inches(1.5), width=Inches(4.5))

            slide = prs.slides.add_slide(content_slide_layout)
            slide.shapes.title.text = "Open Action Items (SCARs/Failures)"
            textbox = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5))
            text_frame = textbox.text_frame
            text_frame.word_wrap = True
            
            supplier_failures = failures[failures['Supplier'] == selected_supplier]
            if not supplier_failures.empty:
                for index, row in supplier_failures.iterrows():
                    p = text_frame.add_paragraph()
                    p.text = f"ID: {row['Failure_ID']} ({row['Status']}) - Part: {row['Part_Number']}, Mode: {row['Failure_Mode']}"
                    p.level = 0
            else:
                p = text_frame.add_paragraph()
                p.text = "No open failures reported for this supplier."

            ppt_buffer = io.BytesIO()
            prs.save(ppt_buffer)
            ppt_buffer.seek(0)
            
            st.success("Report generated successfully!")
            st.download_button(
                label="Download PowerPoint Report",
                data=ppt_buffer,
                file_name=f"SQE_Report_{selected_supplier.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
