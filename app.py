import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date

# 1. UI Setup
st.set_page_config(page_title="Pro Finance", layout="wide")
st.title("📊 ငွေစာရင်း စီမံခန့်ခွဲမှု")

# 2. Connection
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # worksheet name က MyFinanceData ဖြစ်ရပါမယ်
        data = conn.read(worksheet="MyFinanceData", ttl="5s")
        return data
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

# 3. Sidebar Features
st.sidebar.header("⚙️ App Settings")
lang = st.sidebar.selectbox("Language", ["Myanmar", "English"])
monthly_limit = st.sidebar.number_input("Monthly Budget Limit", value=500000)

# 4. Input Section
with st.expander("➕ စာရင်းအသစ်သွင်းရန်", expanded=True):
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_date = st.date_input("Date", date.today())
            t_type = st.radio("အမျိုးအစား", ["Income", "Expense"], horizontal=True)
        with col2:
            t_amt = st.number_input("ပမာဏ (MMK)", min_value=0.0, step=1000.0)
            t_cat = st.selectbox("Category", ["Food", "Salary", "Shopping", "Bills", "Travel", "Health", "Social", "Others"])
        
        t_note = st.text_area("မှတ်ချက် (Note)")
        
        if st.form_submit_button("Cloud ပေါ်သိမ်းမည်"):
            if t_amt > 0:
                new_row = pd.DataFrame([{"Date": str(t_date), "Type": t_type, "Category": t_cat, "Amount": t_amt, "Note": t_note}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # Google Sheet သို့ Update လုပ်ခြင်း
                try:
                    conn.update(worksheet="MyFinanceData", data=updated_df)
                    st.success("စာရင်းသိမ်းပြီးပါပြီ!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}. Sheet name မှန်မမှန်နဲ့ Editor ပေးထားတာ ဟုတ်မဟုတ် ပြန်စစ်ပါ။")
            else:
                st.warning("ပမာဏ ရိုက်ထည့်ပါ")

# 5. Summary & Dashboard
if not df.empty:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    inc = df[df['Type'] == 'Income']['Amount'].sum()
    exp = df[df['Type'] == 'Expense']['Amount'].sum()
    
    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("လက်ကျန်ငွေ", f"{inc-exp:,.0f} ကျပ်")
    m2.metric("ဝင်ငွေ", f"{inc:,.0f}")
    m3.metric("ထွက်ငွေ", f"-{exp:,.0f}")

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("မှတ်တမ်းဇယား")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
    with c2:
        st.subheader("အသုံးစရိတ် ခွဲခြမ်းစိတ်ဖြာမှု")
        exp_df = df[df['Type'] == 'Expense']
        if not exp_df.empty:
            fig = px.pie(exp_df, values='Amount', names='Category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data yet. Google Sheet ထဲမှာ Tab နာမည်ကို MyFinanceData လို့ ပေးထားဖို့ မမေ့ပါနဲ့။")
