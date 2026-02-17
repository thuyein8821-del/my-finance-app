import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import requests
import json
from streamlit_extras.metric_cards import style_metric_cards

# 1. UI Configuration
st.set_page_config(page_title="WealthWise Pro", layout="wide")

# Custom CSS for Modern Look
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTab { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- နေရာ ၂ ခုကို အစားထိုးပေးပါ ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxB2R-mJ0qxexy4sUcoojTeft1gouNvEgvgY-Tdv-dkq62m14kYctB2xXTq1Lkz54QI/exec"
SHEET_ID = "1XwxFHWVnErqOJSkt4lX2HxRHCqH1jdLxwgihhkN-eFo"
# ------------------------------

READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=2)
def load_data():
    try:
        data = pd.read_csv(READ_URL)
        # အမှားမပါအောင် column တွေကို ကိန်းဂဏန်းပြောင်းမယ်
        data['Amount'] = pd.to_numeric(data['Amount'], errors='coerce').fillna(0)
        return data
    except:
        return pd.DataFrame(columns=["ID", "Date", "Type", "Category", "Amount", "Note", "Month_Year"])

df = load_data()

# 2. Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/1077/1077976.png", width=80)
st.sidebar.title("WealthWise Pro")
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Transactions", "Monthly Budget"])

# 3. Logic for Dashboard
if menu == "Dashboard":
    st.title("💹 Financial Overview")
    
    if not df.empty:
        # Metrics Calculations
        total_inc = df[df['Type'] == 'Income']['Amount'].sum()
        total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
        balance = total_inc - total_exp
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Current Balance", f"{balance:,.0f} MMK")
        c2.metric("Total Savings", f"{total_inc:,.0f}", "Income")
        c3.metric("Total Spent", f"{total_exp:,.0f}", "-Expense", delta_color="inverse")
        style_metric_cards(background_color="#FFFFFF", border_left_color="#007bff", border_radius_px=15)

        # Charts Section
        st.write("---")
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("Monthly Trend")
            m_df = df.groupby(['Month_Year', 'Type'])['Amount'].sum().reset_index()
            fig_bar = px.bar(m_df, x='Month_Year', y='Amount', color='Type', barmode='group', template="plotly_white")
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_right:
            st.subheader("Category Split")
            exp_df = df[df['Type'] == 'Expense']
            if not exp_df.empty:
                fig_pie = px.pie(exp_df, values='Amount', names='Category', hole=0.5, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_pie, use_container_width=True)

elif menu == "Transactions":
    st.title("📝 Data Management")
    
    t1, t2 = st.tabs(["Add New", "History & Actions"])
    
    with t1:
        with st.form("entry_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input("Transaction Date")
            t = col1.radio("Type", ["Income", "Expense"], horizontal=True)
            a = col2.number_input("Amount", min_value=0.0)
            c = col2.selectbox("Category", ["Food", "Salary", "Bills", "Shopping", "Transport", "Health", "Social", "Others"])
            n = st.text_input("Note/Description")
            
            if st.form_submit_button("Submit Transaction"):
                if a > 0:
                    payload = {"action": "add", "Date": str(d), "Type": t, "Category": c, "Amount": a, "Note": n}
                    requests.post(SCRIPT_URL, data=json.dumps(payload))
                    st.success("Transaction recorded successfully!")
                    st.rerun()

    with t2:
        if not df.empty:
            st.write("Quick Search:")
            search_term = st.text_input("", placeholder="Search by note or category...")
            filtered_df = df[df.apply(lambda row: search_term.lower() in str(row).lower(), axis=1)]
            st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)
        else:
            st.info("No records found.")

elif menu == "Monthly Budget":
    st.title("🎯 Budget Goal")
    st.info("Coming Soon: Track your monthly spending limits against actual data.")
