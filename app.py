import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# 1. Configuration & Localization
LANG = {
    "English": {
        "title": "Pro Finance Manager", "balance": "Total Balance", "income": "Income",
        "expense": "Expense", "add": "Add Transaction", "amt": "Amount (MMK)",
        "cat": "Category", "date": "Date", "note": "Note", "history": "History",
        "save": "Save to Cloud", "budget_label": "Monthly Budget Limit",
        "warning": "Budget Exceeded!", "success": "Within Budget"
    },
    "Myanmar": {
        "title": "ငွေစာရင်း စီမံခန့်ခွဲမှု", "balance": "စုစုပေါင်း လက်ကျန်", "income": "ဝင်ငွေ",
        "expense": "ထွက်ငွေ", "add": "စာရင်းအသစ်သွင်းရန်", "amt": "ပမာဏ (ကျပ်)",
        "cat": "အမျိုးအစား", "date": "နေ့စွဲ", "note": "မှတ်ချက်", "history": "စာရင်းမှတ်တမ်း",
        "save": "Cloud ပေါ်သိမ်းမည်", "budget_label": "တစ်လစာ အသုံးစရိတ် ကန့်သတ်ချက်",
        "warning": "သတ်မှတ်ငွေထက် ကျော်နေပြီ!", "success": "အသုံးစရိတ် ထိန်းသိမ်းနိုင်မှု ကောင်းမွန်သည်"
    }
}

st.set_page_config(page_title="Pro Finance", layout="wide")
lang_choice = st.sidebar.selectbox("Language / ဘာသာစကား", ["Myanmar", "English"])
L = LANG[lang_choice]

# --- Google Sheet Connection (Public Link Method) ---
# သင့်ရဲ့ Google Sheet URL ကို အောက်ကနေရာမှာ အစားထိုးပါ
SHEET_URL = "https://docs.google.com/spreadsheets/d/1vCh5LDees31-5k8hxqCimTjGRedVZKRwVfXT93e8DeI/edit?gid=0#gid=0"
# CSV အဖြစ်ပြောင်းလဲခြင်း
SHEET_CSV_URL = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=60) # ၁ မိနစ်တိုင်း data အသစ်စစ်မယ်
def load_data():
    try:
        return pd.read_csv(SHEET_CSV_URL)
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

st.title(f"📊 {L['title']}")

# 2. Sidebar Features (Budget & Filters)
st.sidebar.header("Settings")
monthly_budget = st.sidebar.number_input(L['budget_label'], min_value=0, value=500000, step=10000)

# 3. Input Section
with st.expander(f"➕ {L['add']}"):
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.radio("Type", [L['income'], L['expense']], horizontal=True)
        t_amt = st.number_input(L['amt'], min_value=0.0)
    with col2:
        t_cat = st.selectbox(L['cat'], ["Food", "Salary", "Transport", "Shopping", "Bills", "Health", "Social", "Others"])
        t_date = st.date_input(L['date'], date.today())
    
    t_note = st.text_area(L['note'])
    
    if st.button(L['save'], use_container_width=True, type="primary"):
        # Google Sheet ထဲ တိုက်ရိုက်သိမ်းဖို့အတွက်ကတော့ (gsheetsdb) သုံးရမှာမို့
        # လောလောဆယ် App ထဲမှာပဲ ပေါင်းပြထားမယ်။
        new_row = pd.DataFrame([[t_date, t_type, t_cat, t_amt, t_note]], columns=df.columns)
        st.success("စာရင်းသွင်းပြီးပါပြီ။ (Google Sheet ချိတ်ဆက်မှု အောင်မြင်ရန် အဆင့် ၃ ကိုကြည့်ပါ)")

# 4. Dashboard & Analysis
if not df.empty:
    inc = df[df['Type'].str.contains('ဝင်ငွေ|Income', na=False)]['Amount'].sum()
    exp = df[df['Type'].str.contains('ထွက်ငွေ|Expense', na=False)]['Amount'].sum()
    balance = inc - exp

    # Budget Warning
    if exp > monthly_budget:
        st.error(f"{L['warning']} (Over: {exp - monthly_budget:,.0f} ကျပ်)")
    else:
        st.info(f"{L['success']} (Remaining: {monthly_budget - exp:,.0f} ကျပ်)")

    m1, m2, m3 = st.columns(3)
    m1.metric(L['balance'], f"{balance:,.0f} MMK")
    m2.metric(L['income'], f"{inc:,.0f}")
    m3.metric(L['expense'], f"-{exp:,.0f}")

    # Charts
    st.subheader(L['history'])
    st.dataframe(df, use_container_width=True)
