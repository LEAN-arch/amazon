import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly.figure_factory as ff
from sklearn.ensemble import RandomForestClassifier
from prophet import Prophet
from pptx import Presentation
from pptx.util import Inches
import io
import warnings

# --- SUPPRESS DEPRECATION WARNINGS FOR CLEANER PRESENTATION ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


# --- ROBUST STATE CHECK ---
# No st.set_page_config() in sub-pages.
if 'app_data' not in st.session_state:
    st.error("Application data not loaded. Please return to the 'Global Command Center' home page to initialize the app.")
    st.stop()

# Unpack data from the central state dictionary
app_data = st.session_state['app_data']
suppliers = app_data['suppliers']
perf_df = app_data['performance_data']
failures = app_data['failures']

# --- UI RENDER ---
st.markdown("# 🔬 Supplier Deep Dive & Process Control")
st.markdown("This module is the SQE's workbench for monitoring historical performance, analyzing process capability, predicting future outcomes, and taking formal corrective action.")

selected_supplier = st.selectbox("Select a Supplier to Analyze", suppliers['Supplier'].unique(), key="supplier_select_deep_dive")
supplier_data = perf_df[perf_df['Supplier'] == selected_supplier].copy()
supplier_info = suppliers[suppliers['Supplier'] == selected_supplier].iloc[0]

# Reorganized tabs for a logical workflow: Monitor -> Predict -> Act
tab_monitor, tab_predict, tab_act = st.tabs([
    "📊 Process Monitoring (SPC & Cpk)", 
    "🔮 Predictive Analytics (Forecast & ML)", 
    "✍️ Corrective Action & Reporting (SCAR)"
])

# ==============================================================================
# TAB 1: Process Monitoring (SPC & Cpk)
# ==============================================================================
with tab_monitor:
    st.header(f"Process Monitoring for: {selected_supplier}")
    st.markdown("This section analyzes process stability (are we in control?) and capability (can we meet specifications?).")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Process Stability (Control Chart)")
        st.markdown("""
        - **What:** A Statistical Process Control (SPC) chart for a critical parameter.
        - **Why:** It answers the question: "Is the process stable and predictable?" Any point outside the red control limits indicates a 'special cause' variation that must be investigated immediately. This is fundamental to **AS9100 clause 8.5.1.3** (Production process verification).
        """)
        np.random.seed(42)
        spc_data = np.random.normal(loc=10.0, scale=0.15, size=50)
        spc_data[30:35] += 0.6
        fig_spc = go.Figure()
        fig_spc.add_trace(go.Scatter(y=spc_data, mode='lines+markers', name='Measurement'))
        fig_spc.add_hline(y=10.0, line=dict(dash="dash", color="green"), name="Target")
        fig_spc.add_hline(y=10.5, line=dict(dash="dot", color="red"), name="UCL")
        fig_spc.add_hline(y=9.5, line=dict(dash="dot", color="red"), name="LCL")
        fig_spc.update_layout(title="SPC: Gate Oxide Thickness", yaxis_title="Thickness (nm)", xaxis_title="Batch Number")
        st.plotly_chart(fig_spc, use_container_width=True, key="spc_chart")
    
    with col2:
        st.subheader("Process Capability (Cpk)")
        st.markdown("""
        - **What:** A histogram of process measurements plotted against the engineering specification limits (USL/LSL) with the calculated Cpk value.
        - **Why (Actionability):** This is a core Six Sigma metric that answers: "Is the process *capable* of meeting our requirements?" An aerospace industry target is typically **Cpk > 1.33**. A value below this (like the one shown) is a major risk and a data-driven reason to demand process improvement from the supplier, as per **AS9145 (APQP)** requirements.
        """)
        usl, lsl = 10.6, 9.4
        mu, sigma = 10.05, 0.18 # A slightly off-center process with higher variation
        process_data = np.random.normal(mu, sigma, 200)
        
        cpu = (usl - mu) / (3 * sigma)
        cpl = (mu - lsl) / (3 * sigma)
        cpk = min(cpu, cpl)

        fig_cpk = ff.create_distplot([process_data], ['Process Data'], show_hist=True, show_rug=False)
        fig_cpk.add_vline(x=usl, line=dict(dash="dash", color="red"), name="USL")
        fig_cpk.add_vline(x=lsl, line=dict(dash="dash", color="red"), name="LSL")
        fig_cpk.update_layout(title=f"Process Capability: Gate Oxide Thickness (Cpk = {cpk:.2f})")
        st.plotly_chart(fig_cpk, use_container_width=True, key="cpk_chart")
        if cpk < 1.33:
            st.error(f"**Action Required:** Cpk of {cpk:.2f} is below the target of 1.33. This indicates a high risk of producing non-conforming parts. A process improvement plan is required.", icon="🚨")
        else:
            st.success(f"**Process Capable:** Cpk of {cpk:.2f} meets the target of 1.33.", icon="✅")

# ==============================================================================
# TAB 2: Predictive Analytics (Forecast & ML)
# ==============================================================================
with tab_predict:
    st.header("Predictive Analytics for Proactive Quality")
    st.markdown("Using historical data to forecast future performance and predict lot-level outcomes.")

    st.subheader("Future Performance Forecast (Prophet)")
    st.markdown("""
    - **What:** A 30-day forecast of supplier DPPM, with an uncertainty interval.
    - **Why:** This shifts the SQE role from reactive to proactive. The alert system warns of potential threshold breaches weeks in advance, allowing for preventive actions like increased inspections or supplier communication.
    """)
    @st.cache_data
    def run_prophet_forecast(data, metric_col='DPPM', periods=30):
        prophet_df = data[['Date', metric_col]].rename(columns={'Date': 'ds', metric_col: 'y'})
        m = Prophet(daily_seasonality=False, weekly_seasonality=True, yearly_seasonality=True)
        m.fit(prophet_df)
        future = m.make_future_dataframe(periods=periods)
        forecast = m.predict(future)
        return m, forecast
    
    model_prophet, forecast = run_prophet_forecast(supplier_data)
    fig_forecast = go.Figure()
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast', line=dict(color='navy', dash='dash')))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='rgba(0,176,246,0.2)', name='Uncertainty'))
    fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(0,176,246,0.2)'))
    fig_forecast.add_trace(go.Scatter(x=model_prophet.history['ds'], y=model_prophet.history['y'], mode='markers', name='Actuals', marker=dict(color='black', size=4)))
    fig_forecast.update_layout(title=f"30-Day DPPM Forecast for {selected_supplier}", yaxis_title="DPPM")
    st.plotly_chart(fig_forecast, use_container_width=True, key="prophet_forecast_chart")
    
    st.subheader("Predictive Lot Disposition (ML Classifier)")
    st.markdown("""
    - **What:** An interactive ML model that predicts the failure probability of an incoming lot based on its process parameters.
    - **Why:** This enables a "smarter" incoming inspection (IQC) strategy. Instead of sampling all lots equally, we can allocate more stringent testing to lots the model flags as high-risk, optimizing resources and improving escape detection.
    """)
    @st.cache_data
    def get_model_and_data():
        np.random.seed(42)
        X = pd.DataFrame({'Temp_Avg': np.random.normal(150, 5, 200), 'Pressure_Var': np.random.gamma(1, 0.5, 200), 'Vibration_Max': np.random.uniform(0.1, 1.0, 200)})
        y = ((X['Temp_Avg'] > 155) | (X['Pressure_Var'] > 1.2) | (X['Vibration_Max'] > 0.8)).astype(int)
        y = y & (np.random.rand(200) < 0.7)
        model = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, y)
        return model, X.describe()
    model_rf, X_desc = get_model_and_data()
    col1, col2 = st.columns([1, 2])
    with col1:
        temp = st.slider("Average Temp (°C)", float(X_desc.loc['min','Temp_Avg']), float(X_desc.loc['max','Temp_Avg']), 152.0, 0.1, key="slider_temp")
        pressure = st.slider("Pressure Variance (psi)", float(X_desc.loc['min','Pressure_Var']), float(X_desc.loc['max','Pressure_Var']), 0.8, 0.01, key="slider_pressure")
        vibration = st.slider("Max Vibration (g)", float(X_desc.loc['min','Vibration_Max']), float(X_desc.loc['max','Vibration_Max']), 0.5, 0.01, key="slider_vibration")
    with col2:
        input_data = pd.DataFrame([[temp, pressure, vibration]], columns=['Temp_Avg', 'Pressure_Var', 'Vibration_Max'])
        fail_prob = model_rf.predict_proba(input_data)[0, 1]
        if fail_prob > 0.6: st.error(f"**High Risk ({fail_prob:.0%})** - Recommend placing lot on hold for engineering review.", icon="🚨")
        elif fail_prob > 0.3: st.warning(f"**Medium Risk ({fail_prob:.0%})** - Recommend enhanced inspection (per **ANSI Z1.4**).", icon="⚠️")
        else: st.success(f"**Low Risk ({fail_prob:.0%})** - Recommend standard release protocol.", icon="✅")
        st.progress(fail_prob)
    
    with st.expander("SME Insights: Model Validation for Aerospace Applications"):
        st.markdown("""
        In a mission-critical context like Kuiper, deploying an ML model requires rigorous validation beyond just accuracy.
        - **Confusion Matrix:** We must understand the trade-off between False Positives (flagging a good lot as bad) and False Negatives (letting a bad lot pass). For aerospace, minimizing **False Negatives** is paramount.
        - **Precision vs. Recall:** We would tune the model's decision threshold to maximize **Recall** (the ability to find all actual positive/bad lots), even if it means lowering Precision and having more False Positives to review manually.
        - **Model Drift:** The model's performance must be continuously monitored to ensure its predictions remain accurate as supplier processes change over time.
        """)

# ==============================================================================
# TAB 3: Corrective Action & Reporting (SCAR)
# ==============================================================================
with tab_act:
    st.header("Formal Corrective Action & Reporting")
    st.markdown("""
    - **What:** A tool to generate a pre-formatted **Supplier Corrective Action Request (SCAR)** based on the data and analysis from this dashboard.
    - **Why:** This automates a critical communication workflow. A formal SCAR is a key part of any **ISO 9001 / AS9100** compliant quality system. This tool ensures that requests for corrective action are always data-driven, professional, and standardized.
    """)
    st.subheader("Generate Supplier Corrective Action Request (SCAR)")
    non_conformance_details = st.text_area("Describe the Non-Conformance (Be specific)", "During incoming inspection of Lot #A-LOT-7891, 15 out of 1000 units exhibited wire bond lift failures on Pad 14, resulting in a lot rejection.")
    standard_ref = st.selectbox("Reference to Quality Standard Requirement", ["AS9100D Clause 8.4.3: Information for External Providers", "IPC-A-610 Class 3: Acceptance Criteria for Wire Bonds", "JEDEC JESD22-B116: Wire Bond Shear Test Method", "IATF 16949 Clause 8.7.1.4: Control of Reworked Product"])
    
    # We need a figure to embed in the report, let's create it here
    fig_dppm_report = go.Figure()
    fig_dppm_report.add_trace(go.Scatter(x=supplier_data['Date'], y=supplier_data['DPPM'], mode='lines', name='Daily DPPM', line=dict(color='red')))
    fig_dppm_report.update_layout(title="DPPM Trend for Reference", yaxis_title="DPPM")

    if st.button("Generate SCAR PowerPoint"):
        with st.spinner("Creating SCAR..."):
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[0])
            slide.shapes.title.text = "Supplier Corrective Action Request (SCAR)"
            slide.placeholders[1].text = f"To: {selected_supplier}\nSCAR ID: KUI-SCAR-2023-017"
            
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = "SCAR Details & Objective Evidence"
            
            txBox = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(4), Inches(1)); tf = txBox.text_frame; tf.text = "Non-Conformance Description:"; tf.paragraphs[0].font.bold = True
            txBox2 = slide.shapes.add_textbox(Inches(0.5), Inches(2.2), Inches(4), Inches(2)); tf2 = txBox2.text_frame; tf2.text = non_conformance_details
            
            txBox3 = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(4), Inches(1)); tf3 = txBox3.text_frame; tf3.text = "Requirement Reference:"; tf3.paragraphs[0].font.bold = True
            txBox4 = slide.shapes.add_textbox(Inches(0.5), Inches(5.2), Inches(4), Inches(1)); tf4 = txBox4.text_frame; tf4.text = standard_ref
            
            dppm_img_bytes = fig_dppm_report.to_image(format="png", width=800, height=450)
            slide.shapes.add_picture(io.BytesIO(dppm_img_bytes), Inches(4.7), Inches(1.7), width=Inches(5))
            
            slide = prs.slides.add_slide(prs.slide_layouts[5])
            slide.shapes.title.text = "Action Required from Supplier"
            txBox_action = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(8), Inches(5)); tf_action = txBox_action.text_frame
            tf_action.text = "Please provide the following within 14 calendar days:\n\n"
            p1 = tf_action.add_paragraph(); p1.text = "1. Interim Containment Action."; p1.level = 1
            p2 = tf_action.add_paragraph(); p2.text = "2. Completed 8D Root Cause Analysis."; p2.level = 1
            p3 = tf_action.add_paragraph(); p3.text = "3. Proposed Corrective and Preventive Actions."; p3.level = 1
            p4 = tf_action.add_paragraph(); p4.text = "4. Plan for implementation and validation of actions."; p4.level = 1
            
            ppt_buffer = io.BytesIO(); prs.save(ppt_buffer); ppt_buffer.seek(0)
            
            st.success("SCAR generated successfully!")
            st.download_button(
                label="Download SCAR (.pptx)", data=ppt_buffer,
                file_name=f"SCAR_{selected_supplier.replace(' ', '_')}_{pd.Timestamp.now().strftime('%Y%m%d')}.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
