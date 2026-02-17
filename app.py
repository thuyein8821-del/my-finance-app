import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import requests

# 1. UI Configuration
st.set_page_config(page_title="Pro Finance Manager", layout="wide")

# 2. Sidebar Settings
st.sidebar.title("⚙️ Settings")
lang = st.sidebar.selectbox("Language", ["Myanmar", "English"])
L = {
    "title": "ငွေစာရင်း စီမံခန့်ခွဲမှု" if lang == "Myanmar" else "Pro Finance Manager",
    "add": "စာရင်းအသစ်သွင်းရန်" if lang == "Myanmar" else "Add Transaction",
    "save": "Cloud ပေါ်သိမ်းမည်" if lang == "Myanmar" else "Save to Cloud",
    "history": "မှတ်တမ်းများ" if lang == "Myanmar" else "History"
}

st.title(f"📊 {L['title']}")

# --- Google Sheet Connection Setup ---
# Secrets ထဲက Link ကို ယူမယ်
try:
    SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # URL ကို CSV format ပြောင်းပြီး ဖတ်မယ် (ဒါက error အကင်းဆုံးနည်းပါ)
    CSV_URL = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv&gid=0').replace('/edit#gid=0', '/export?format=csv&gid=0')
except:
    st.error("Secrets ထဲမှာ Google Sheet Link ထည့်ဖို့ လိုအပ်နေပါတယ်။")
    st.stop()

@st.cache_data(ttl=5)
def load_data():
    try:
        data = pd.read_csv(CSV_URL)
        return data
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

# 3. Input Form
with st.expander(f"➕ {L['add']}", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t_date = st.date_input("Date", date.today())
            t_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
            t_amt = st.number_input("Amount", min_value=0.0, step=1000.0)
        with c2:
            t_cat = st.selectbox("Category", ["Food", "Salary", "Shopping", "Bills", "Travel", "Health", "Social", "Others"])
            t_note = st.text_area("Note")
        
        if st.form_submit_button(L['save']):
            if t_amt > 0:
                # ဒေတာအသစ်ကို Google Sheet ထဲပို့ဖို့ပြင်ဆင်ခြင်း
                # မှတ်ချက် - ဒီနေရာမှာ 'gsheets_connection' ရဲ့ update error ကိုကျော်ဖို့
                # အလွယ်ကူဆုံးနည်းလမ်းက Google Form သို့မဟုတ် ပိုကောင်းတဲ့ Connection သုံးတာပါ။
                # လောလောဆယ် error ရှင်းဖို့အတွက် အောက်ပါအတိုင်း ပြင်ပါမယ်။
                
                from streamlit_gsheets import GSheetsConnection
                conn = st.connection("gsheets", type=GSheetsConnection)
                
                new_row = pd.DataFrame([{"Date": str(t_date), "Type": t_type, "Category": t_cat, "Amount": t_amt, "Note": t_note}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                try:
                    conn.update(worksheet="MyFinanceData", data=updated_df)
                    st.success("Successfully Saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}. Google Sheet မှာ Editor ပေးထားတာ သေချာရဲ့လား ပြန်စစ်ပေးပါ။")
            else:
                st.warning("ပမာဏ ရိုက်ထည့်ပါ")

# 4. Dashboard
if not df.empty:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    inc = df[df['Type'] == 'Income']['Amount'].sum()
    exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Balance", f"{inc-exp:,.0f} MMK")
    m2.metric("Income", f"{inc:,.0f}")
    m3.metric("Expense", f"-{exp:,.0f}")

    st.subheader(L['history'])
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    
    # Simple Chart
    if not df[df['Type'] == 'Expense'].empty:
        fig = px.pie(df[df['Type'] == 'Expense'], values='Amount', names='Category', title="Expense Analysis")
        st.plotly_chart(fig, use_container_width=True)
