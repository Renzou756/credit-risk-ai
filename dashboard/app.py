import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="Credit Risk AI",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .risk-high {
        background-color: #ff6b6b;
        padding: 10px;
        border-radius: 5px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .risk-low {
        background-color: #51cf66;
        padding: 10px;
        border-radius: 5px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .probability-gauge {
        text-align: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏦 Credit Risk Prediction Dashboard</div>', unsafe_allow_html=True)

# API configuration
API_URL = "http://127.0.0.1:8000/predict"

def create_loan_form():
    """Create the loan application input form"""
    st.header("📝 Loan Application Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Financial Information")
        loan_amnt = st.number_input("Loan Amount ($)", min_value=1000, max_value=50000, value=10000, step=500)
        int_rate = st.slider("Interest Rate (%)", min_value=5.0, max_value=30.0, value=12.5, step=0.1)
        installment = st.number_input("Monthly Installment ($)", min_value=100, max_value=1500, value=350, step=10)
        annual_inc = st.number_input("Annual Income ($)", min_value=20000, max_value=200000, value=75000, step=5000)
        dti = st.slider("Debt-to-Income Ratio", min_value=0.0, max_value=40.0, value=15.5, step=0.1)
    
    with col2:
        st.subheader("Credit History")
        revol_bal = st.number_input("Revolving Balance ($)", min_value=0, max_value=50000, value=15000, step=500)
        revol_util = st.slider("Revolving Utilization (%)", min_value=0.0, max_value=100.0, value=45.2, step=0.1)
        total_acc = st.number_input("Total Credit Accounts", min_value=1, max_value=100, value=25)
        open_acc = st.number_input("Open Accounts", min_value=1, max_value=50, value=10)
        pub_rec = st.number_input("Public Records", min_value=0, max_value=10, value=0)
        inq_last_6mths = st.number_input("Inquiries (6 months)", min_value=0, max_value=10, value=2)
        delinq_2yrs = st.number_input("Delinquencies (2 years)", min_value=0, max_value=10, value=0)
    
    with col3:
        st.subheader("Personal & Loan Details")
        emp_length = st.selectbox("Employment Length", 
            ["< 1 year", "1 year", "2 years", "3 years", "4 years", "5 years", 
             "6 years", "7 years", "8 years", "9 years", "10+ years"])
        verification_status = st.selectbox("Verification Status", 
            ["Verified", "Source Verified", "Not Verified"])
        home_ownership = st.selectbox("Home Ownership", 
            ["MORTGAGE", "RENT", "OWN", "NONE"])
        purpose = st.selectbox("Loan Purpose", 
            ["debt_consolidation", "credit_card", "home_improvement", "other", 
             "major_purchase", "medical", "small_business", "vacation", "wedding"])
        grade = st.selectbox("Loan Grade", ["A", "B", "C", "D", "E", "F", "G"])
        sub_grade = st.selectbox("Loan Sub-grade", 
            [f"{grade}{i}" for i in range(1, 6)])
        addr_state = st.selectbox("State", ["CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"])
        term_months = st.radio("Loan Term", [36, 60], horizontal=True)
        fico_avg = st.slider("FICO Score", min_value=300, max_value=850, value=680, step=10)
    
    # Calculated fields (you can make these more sophisticated)
    credit_age = st.slider("Credit History Age (years)", min_value=1.0, max_value=30.0, value=8.5, step=0.5)
    payment_to_income = installment / (annual_inc / 12) if annual_inc > 0 else 0
    revol_utilization_trend = st.slider("Revolving Utilization Trend", min_value=-10.0, max_value=10.0, value=0.1, step=0.1)
    
    # Log transformations (calculated automatically)
    log_annual_inc = np.log(annual_inc) if annual_inc > 0 else 0
    log_loan_amnt = np.log(loan_amnt) if loan_amnt > 0 else 0
    log_revol_bal = np.log(revol_bal) if revol_bal > 0 else 0
    
    # Current date for issue_d
    issue_d = st.date_input("Application Date", value=datetime.now())
    
    return {
        "loan_amnt": float(loan_amnt),
        "int_rate": float(int_rate),
        "installment": float(installment),
        "annual_inc": float(annual_inc),
        "dti": float(dti),
        "revol_bal": float(revol_bal),
        "revol_util": float(revol_util),
        "total_acc": int(total_acc),
        "open_acc": int(open_acc),
        "pub_rec": int(pub_rec),
        "inq_last_6mths": int(inq_last_6mths),
        "delinq_2yrs": int(delinq_2yrs),
        "emp_length": emp_length,
        "verification_status": verification_status,
        "home_ownership": home_ownership,
        "purpose": purpose,
        "grade": grade,
        "sub_grade": sub_grade,
        "addr_state": addr_state,
        "issue_d": issue_d.strftime("%Y-%m-%d"),
        "credit_age": float(credit_age),
        "payment_to_income": float(payment_to_income),
        "revol_utilization_trend": float(revol_utilization_trend),
        "log_annual_inc": float(log_annual_inc),
        "log_loan_amnt": float(log_loan_amnt),
        "log_revol_bal": float(log_revol_bal),
        "term_months": int(term_months),
        "fico_avg": float(fico_avg)
    }

def create_gauge_chart(probability):
    """Create a gauge chart for probability visualization"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = probability * 100,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Default Probability (%)", 'font': {'size': 24}},
        delta = {'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': 'lightgreen'},
                {'range': [30, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'red'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90}}))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def create_shap_plot(shap_values):
    """Create a horizontal bar chart for SHAP values"""
    # Sort features by absolute impact
    features = list(shap_values.keys())
    values = list(shap_values.values())
    
    # Create DataFrame and sort
    df_shap = pd.DataFrame({'feature': features, 'impact': values})
    df_shap['abs_impact'] = df_shap['impact'].abs()
    df_shap = df_shap.sort_values('abs_impact', ascending=True).tail(15)  # Top 15 features
    
    # Create plot
    fig = px.bar(df_shap, 
                 x='impact', 
                 y='feature', 
                 orientation='h',
                 title="Top Feature Impacts on Prediction",
                 color=df_shap['impact'],
                 color_continuous_scale='RdBu',
                 color_continuous_midpoint=0)
    
    fig.update_layout(
        yaxis_title="Features",
        xaxis_title="SHAP Impact (Positive increases default risk)",
        height=400,
        showlegend=False
    )
    
    return fig

def main():
    # Create loan form
    loan_data = create_loan_form()
    
    # Predict button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_btn = st.button("🚀 Predict Default Risk", type="primary", use_container_width=True)
    
    if predict_btn:
        try:
            with st.spinner("Analyzing loan application..."):
                # Make API call
                response = requests.post(API_URL, json=loan_data)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display results
                    st.success("Prediction completed successfully!")
                    
                    # Results in columns
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Probability gauge
                        st.plotly_chart(create_gauge_chart(result["default_probability"]), use_container_width=True)
                        
                        # Risk level
                        prob_percent = result["default_probability"] * 100
                        risk_class = "risk-high" if result["risk_level"] == "HIGH" else "risk-low"
                        st.markdown(f'<div class="{risk_class}">Risk Level: {result["risk_level"]}</div>', unsafe_allow_html=True)
                        
                        # Recommendation
                        if result["risk_level"] == "HIGH":
                            st.error("🚨 Recommendation: Consider declining or requesting additional collateral")
                        else:
                            st.success("✅ Recommendation: Loan appears acceptable")
                    
                    with col2:
                        # SHAP explanations
                        st.plotly_chart(create_shap_plot(result["shap_values"]), use_container_width=True)
                    
                    # Detailed feature impacts
                    with st.expander("📊 Detailed Feature Analysis"):
                        shap_df = pd.DataFrame({
                            'Feature': list(result["shap_values"].keys()),
                            'Impact': list(result["shap_values"].values())
                        })
                        shap_df['Absolute_Impact'] = shap_df['Impact'].abs()
                        shap_df = shap_df.sort_values('Absolute_Impact', ascending=False)
                        
                        st.dataframe(shap_df.head(10), use_container_width=True)
                        
                        # Interpretation
                        st.info("""
                        **How to interpret SHAP values:**
                        - 🔴 **Positive values** increase default probability
                        - 🟢 **Negative values** decrease default probability  
                        - 📊 **Larger absolute values** have bigger impact
                        """)
                
                else:
                    st.error(f"API Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to prediction API. Make sure your FastAPI server is running on http://127.0.0.1:8000")
        except Exception as e:
            st.error(f"❌ Prediction failed: {str(e)}")

    # Sidebar with information
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown("""
        This dashboard predicts the probability of loan default using machine learning.
        
        **Features:**
        - 🏦 XGBoost model trained on historical loan data
        - 📊 SHAP explanations for transparent decisions
        - 📈 Real-time risk assessment
        - 🎯 73.96% AUC accuracy
        
        **How to use:**
        1. Fill in loan details
        2. Click 'Predict Default Risk'
        3. Review probability and explanations
        """)
        
        st.header("🔧 API Status")
        try:
            response = requests.get(API_URL.replace("/predict", "/health"), timeout=5)
            if response.status_code == 200:
                st.success("✅ API Connected")
            else:
                st.warning("⚠️ API Response Unexpected")
        except:
            st.error("❌ API Not Connected")

if __name__ == "__main__":
    import numpy as np
    main()