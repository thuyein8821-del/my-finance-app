import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import requests
import json

# 1. Page Configuration
st.set_page_config(page_title="Pro Finance Manager", layout="wide")
st.title("📊 ငွေစာရင်း စီမံခန့်ခွဲမှု")

# --- နေရာ ၂ ခုကို အစားထိုးပေးပါ ---
# အဆင့် ၁ မှာရလာတဲ့ Web App URL ကို ဒီမှာထည့်ပါ
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwlongMNbfOQ9Pl2uHshbSYqAMtxaUrSVI5YvPwD5_VIc_cqT9QYeocdtNjNf7IQlYblw/exec"
# သင့် Google Sheet URL ထဲက ID ကို ဒီမှာထည့်ပါ
SHEET_ID = "1vCh5LDees31-5k8hxqCimTjGRedVZKRwVfXT93e8DeI" 
# ------------------------------

READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=5)
def load_data():
    try:
        data = pd.read_csv(READ_URL)
        return data
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

# Input Form
with st.expander("➕ စာရင်းအသစ်သွင်းရန်", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t_date = st.date_input("Date", date.today())
            t_type = st.radio("အမျိုးအစား", ["Income", "Expense"], horizontal=True)
            t_amt = st.number_input("ပမာဏ (MMK)", min_value=0.0)
        with c2:
            t_cat = st.selectbox("Category", ["Food", "Salary", "Shopping", "Bills", "Health", "Others"])
            t_note = st.text_area("မှတ်ချက်")
        
        if st.form_submit_button("Cloud ပေါ်သိမ်းမည်"):
            if t_amt > 0:
                payload = {
                    "Date": str(t_date),
                    "Type": t_type,
                    "Category": t_cat,
                    "Amount": t_amt,
                    "Note": t_note
                }
                # Google App Script သို့ ဒေတာပို့ခြင်း
                try:
                    response = requests.post(SCRIPT_URL, data=json.dumps(payload))
                    if response.status_code == 200:
                        st.success("စာရင်းသိမ်းပြီးပါပြီ!")
                        st.rerun()
                    else:
                        st.error("ပို့လို့မရပါဘူး။ URL ကို ပြန်စစ်ပါ။")
                except Exception as e:
                    st.error(f"Error: {e}")

# Summary & Table
if not df.empty:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    inc = df[df['Type'] == 'Income']['Amount'].sum()
    exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("လက်ကျန်ငွေ", f"{inc-exp:,.0f} ကျပ်")
    m2.metric("ဝင်ငွေ", f"{inc:,.0f}")
    m3.metric("ထွက်ငွေ", f"-{exp:,.0f}")
    
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
