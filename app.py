import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date

# 1. UI Configuration
st.set_page_config(page_title="Pro Finance Manager", layout="wide")

# 2. Localization
lang = st.sidebar.selectbox("Language / ဘာသာစကား", ["Myanmar", "English"])
L = {
    "title": "ငွေစာရင်း စီမံခန့်ခွဲမှု" if lang == "Myanmar" else "Pro Finance Manager",
    "add": "စာရင်းအသစ်သွင်းရန်" if lang == "Myanmar" else "Add Transaction",
    "save": "Cloud ပေါ်သိမ်းမည်" if lang == "Myanmar" else "Save to Cloud",
    "history": "မှတ်တမ်းများ" if lang == "Myanmar" else "History",
    "type": "အမျိုးအစား" if lang == "Myanmar" else "Type",
    "amt": "ပမာဏ" if lang == "Myanmar" else "Amount",
    "cat": "အမျိုးအစား" if lang == "Myanmar" else "Category",
    "note": "မှတ်ချက်" if lang == "Myanmar" else "Note"
}

st.title(f"📊 {L['title']}")

# 3. Google Sheets Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Sheet ထဲက data ကိုဖတ်မယ်
        data = conn.read(ttl="10s") 
        # အကယ်၍ data ထဲမှာ Type column မပါရင် error မတက်အောင် empty dataframe ပြန်ပေးမယ်
        if 'Type' not in data.columns:
            return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])
        return data
    except Exception as e:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

# 4. Input Form
with st.expander(f"➕ {L['add']}", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_date = st.date_input("Date", date.today())
            t_type = st.radio(L['type'], ["Income", "Expense"], horizontal=True)
            t_amt = st.number_input(L['amt'], min_value=0.0, step=1000.0)
        with col2:
            t_cat = st.selectbox(L['cat'], ["Food", "Salary", "Shopping", "Bills", "Travel", "Health", "Others"])
            t_note = st.text_area(L['note'])
        
        if st.form_submit_button(L['save']):
            if t_amt > 0:
                new_entry = pd.DataFrame([{"Date": t_date.strftime("%Y-%m-%d"), "Type": t_type, 
                                          "Category": t_cat, "Amount": t_amt, "Note": t_note}])
                # ရှိပြီးသား data နဲ့ ပေါင်းမယ်
                updated_df = pd.concat([df, new_entry], ignore_index=True)
                conn.update(data=updated_df)
                st.success("Saved Successfully!")
                st.rerun()

# 5. Dashboard
if not df.empty and 'Type' in df.columns:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    inc = df[df['Type'] == 'Income']['Amount'].sum()
    exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Balance", f"{inc-exp:,.0f} MMK")
    m2.metric("Income", f"{inc:,.0f}")
    m3.metric("Expense", f"-{exp:,.0f}")

    st.subheader(L['history'])
    st.dataframe(df, use_container_width=True)
else:
    st.info("No data yet. Google Sheet ထဲမှာ Date, Type, Category, Amount, Note ခေါင်းစဉ်တွေ ရှိမရှိ စစ်ပေးပါ။")
