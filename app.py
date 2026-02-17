import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

# 1. Configuration & Localization
LANG = {
    "English": {
        "title": "Pro Finance Manager", "balance": "Total Balance", "income": "Income",
        "expense": "Expense", "add": "Add Transaction", "amt": "Amount (MMK)",
        "cat": "Category", "date": "Date", "note": "Note", "history": "History",
        "save": "Save Data", "del": "Delete Last", "dl": "Download Excel/CSV",
        "budget_label": "Monthly Budget", "analysis": "Spending Analysis"
    },
    "Myanmar": {
        "title": "ငွေစာရင်း စီမံခန့်ခွဲမှု", "balance": "စုစုပေါင်း လက်ကျန်", "income": "ဝင်ငွေ",
        "expense": "ထွက်ငွေ", "add": "စာရင်းအသစ်သွင်းရန်", "amt": "ပမာဏ (ကျပ်)",
        "cat": "အမျိုးအစား", "date": "နေ့စွဲ", "note": "မှတ်ချက်", "history": "မှတ်တမ်းများ",
        "save": "သိမ်းဆည်းမည်", "del": "နောက်ဆုံးစာရင်းဖျက်ရန်", "dl": "Excel ထုတ်ယူရန်",
        "budget_label": "တစ်လစာ အသုံးစရိတ်သတ်မှတ်ချက်", "analysis": "အသုံးစရိတ် ခွဲခြမ်းစိတ်ဖြာမှု"
    }
}

st.set_page_config(page_title="Pro Finance", layout="wide", initial_sidebar_state="collapsed")
lang_choice = st.sidebar.selectbox("Language / ဘာသာစကား", ["Myanmar", "English"])
L = LANG[lang_choice]

# 2. Data Persistence (GitHub မှာဆိုရင် CSV က Session ပိတ်ရင် ပျောက်တတ်ပေမဲ့ 
# Streamlit Cloud မှာ ပိုငြိမ်ပါတယ်။)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

st.title(f"📊 {L['title']}")

# 3. Input Section (Feature စုံ)
with st.expander(f"➕ {L['add']}", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        t_type = st.radio("Type", [L['income'], L['expense']], horizontal=True)
        t_amt = st.number_input(L['amt'], min_value=0.0, step=1000.0)
        t_cat = st.selectbox(L['cat'], ["Food", "Salary", "Transport", "Shopping", "Bills", "Health", "Social", "Others"])
    with col2:
        t_date = st.date_input(L['date'], date.today())
        t_note = st.text_area(L['note'], placeholder="မှတ်ချက်ရေးရန်...")
    
    if st.button(L['save'], use_container_width=True, type="primary"):
        new_row = pd.DataFrame([[t_date, t_type, t_cat, t_amt, t_note]], columns=st.session_state.df.columns)
        st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
        st.balloons()
        st.rerun()

# 4. Dashboard Logic
df = st.session_state.df
if not df.empty:
    # Calculation
    total_inc = df[df['Type'] == L['income']]['Amount'].sum()
    total_exp = df[df['Type'] == L['expense']]['Amount'].sum()
    balance = total_inc - total_exp

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(L['balance'], f"{balance:,.0f} MMK", delta=f"{balance:,.0f}")
    m2.metric(L['income'], f"{total_inc:,.0f}")
    m3.metric(L['expense'], f"-{total_exp:,.0f}")

    # Charts & History
    c1, c2 = st.columns([1.2, 0.8])
    with c1:
        st.subheader(f"📜 {L['history']}")
        st.dataframe(df.sort_index(ascending=False), use_container_width=True)
        if st.button(L['del']):
            st.session_state.df = st.session_state.df[:-1]
            st.rerun()
    with c2:
        st.subheader(f"🎯 {L['analysis']}")
        exp_df = df[df['Type'] == L['expense']]
        if not exp_df.empty:
            fig = px.pie(exp_df, values='Amount', names='Category', hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses to analyze yet.")

    # Sidebar Tools
    st.sidebar.markdown(f"### {L['dl']}")
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("Download CSV", csv, "my_finance.csv", "text/csv")
else:
    st.info("No data recorded yet. Please add a transaction above.")
