"""Module 6 — Streamlit demo: bank-staff churn lookup tool. Calls the FastAPI /predict."""
import os, requests, streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="Churn Lookup", page_icon="🏦")
st.title("🏦 Customer Churn Lookup")
st.caption("Bank-staff tool — enter a customer profile to get churn risk + segment.")

with st.form("lookup"):
    c1, c2 = st.columns(2)
    age = c1.number_input("Age", 18, 100, 40)
    balance = c2.number_input("Balance", 0.0, value=50000.0)
    freq = c1.number_input("Txn frequency (6m)", 0.0, value=60.0)
    complaints = c2.number_input("Complaints (6m)", 0.0, value=1.0)
    country = c1.selectbox("Country", ["France", "Germany", "Spain"])
    gender = c2.selectbox("Gender", ["Male", "Female"])
    submit = st.form_submit_button("Predict")

if submit:
    payload = dict(age=age, balance=balance, frequency=freq, complaints_sum=complaints,
                   country=country, gender=gender)
    try:
        r = requests.post(f"{API}/predict", json=payload, timeout=10).json()
        st.metric("Churn probability", f"{r['churn_probability']:.1%}")
        st.write("**Risk label:**", "⚠️ At risk" if r["churn_label"] else "✅ Stable")
        if r.get("segment") is not None:
            st.write("**Segment:**", r["segment"])
        st.caption(f"model_source={r['model_source']} · threshold={r['threshold']}")
    except Exception as e:
        st.error(f"API not reachable: {e}")
