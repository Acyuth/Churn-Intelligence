import streamlit as st
import pandas as pd
import pickle
from pathlib import Path

# --- PAGE SETUP ---
st.set_page_config(page_title="KKBOX Churn AI", page_icon="🎧", layout="centered")

st.title("🎧 KKBOX Customer Retention Engine")
st.markdown("Modify user behavior parameters to simulate churn risk and determine intervention strategy.")
st.divider()

# --- LOAD MODEL ---
# @st.cache_resource ensures the heavy model only loads once, keeping the app fast
@st.cache_resource
def load_model():
    model_path = Path("outputs/xgboost_churn_model.pkl")
    features_path = Path("outputs/feature_names.pkl")
    
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(features_path, "rb") as f:
        feature_names = pickle.load(f)
        
    return model, feature_names

try:
    model, feature_names = load_model()
except FileNotFoundError:
    st.error("Model files not found. Make sure you are running the app from the root 'churn-intelligence' folder.")
    st.stop()

# --- USER INPUTS (Based on top SHAP features) ---
st.subheader("User Behavior & Profile")

col1, col2 = st.columns(2)

with col1:
    auto_renew = st.radio("Auto-Renew is ON?", ["Yes", "No"])
    cancel_flag = st.radio("Clicked Cancel Recently?", ["Yes", "No"])
    age = st.number_input("Age", min_value=10, max_value=80, value=25)
    city = st.number_input("City Code", min_value=1, max_value=22, value=1)

with col2:
    lifetime_spend = st.number_input("Total Lifetime Spend (NTD)", min_value=0, value=1500)
    listen_seconds = st.number_input("Total Listening Seconds", min_value=0, value=50000)
    songs_completed = st.number_input("Total Songs Completed", min_value=0, value=200)
    registered_via = st.selectbox("Registration Method", [3, 4, 7, 9, 13])

# Map UI inputs to 1s and 0s for the model
user_data = {
    'auto_renew_flag': 1 if auto_renew == "Yes" else 0,
    'cancel_flag': 1 if cancel_flag == "Yes" else 0,
    'age': age,
    'city': city,
    'total_lifetime_spend': lifetime_spend,
    'total_listening_seconds': listen_seconds,
    'total_songs_completed': songs_completed,
    'registered_via': registered_via
}

# The model expects ALL original columns. We fill any missing ones with 0.
model_inputs = {}
for col in feature_names:
    model_inputs[col] = user_data.get(col, 0)

input_df = pd.DataFrame([model_inputs])

# --- PREDICTION ENGINE ---
st.divider()

if st.button("Calculate Churn Risk", type="primary", use_container_width=True):
    # predict_proba returns [Probability of Retaining, Probability of Churning]
    churn_prob = model.predict_proba(input_df)[0][1] * 100
    
    if churn_prob > 50:
        st.error(f"### 🚨 High Risk of Churn: {churn_prob:.1f}%")
        st.write("**Strategy Recommendation:** This user is highly likely to leave. Deploy the $30 retention intervention immediately.")
    else:
        st.success(f"### ✅ Safe Customer: {churn_prob:.1f}% Risk")
        st.write("**Strategy Recommendation:** Customer is healthy. Do not offer discounts to avoid unnecessary margin loss.")