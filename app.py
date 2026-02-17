import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import requests
import json

st.set_page_config(page_title="Pro Finance Manager", layout="wide")

# --- နေရာ ၂ ခုကို အစားထိုးပေးပါ ---
SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxekiLg67GTAv0oiERc28Rr0TgxCwRGj6ptRA5y4OQEo7udbMIPnVe8rao82kVey2DLMQ/exec"
SHEET_ID = "1vCh5LDees31-5k8hxqCimTjGRedVZKRwVfXT93e8DeI"
# ------------------------------

READ_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=5)
def load_data():
    try:
        return pd.read_csv(READ_URL)
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

st.title("💰 Pro Finance Manager")

# Sidebar Summary
st.sidebar.title("📊 Dashboard")
if not df.empty:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    total_inc = df[df['Type'] == 'Income']['Amount'].sum()
    total_exp = df[df['Type'] == 'Expense']['Amount'].sum()
    st.sidebar.metric("လက်ကျန်ငွေ", f"{total_inc - total_exp:,.0f} MMK")
    st.sidebar.progress(min(total_exp/total_inc, 1.0) if total_inc > 0 else 0)

# Tabs for Features
tab1, tab2, tab3 = st.tabs(["➕ စာရင်းသွင်း/ပြင်ဆင်", "📜 မှတ်တမ်းများ", "📈 ခွဲခြမ်းစိတ်ဖြာမှု"])

with tab1:
    st.subheader("စာရင်းအသစ်သွင်းရန် သို့မဟုတ် ပြင်ဆင်ရန်")
    
    # ပြင်ဆင်ဖို့အတွက် ရွေးချယ်မှု
    edit_mode = st.toggle("Edit Mode (ပြင်ဆင်ရန်)")
    selected_index = None
    default_vals = {"date": date.today(), "type": "Expense", "amt": 0.0, "cat": "Food", "note": ""}

    if edit_mode and not df.empty:
        selected_index = st.selectbox("ပြင်ချင်သည့် အစဉ်နံပါတ် (Row)", range(len(df)), format_func=lambda x: f"Row {x}: {df.iloc[x]['Date']} - {df.iloc[x]['Category']}")
        row = df.iloc[selected_index]
        default_vals = {"date": pd.to_datetime(row['Date']).date(), "type": row['Type'], "amt": float(row['Amount']), "cat": row['Category'], "note": row['Note']}

    with st.form("main_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        t_date = c1.date_input("Date", default_vals["date"])
        t_type = c1.radio("Type", ["Income", "Expense"], index=0 if default_vals["type"]=="Income" else 1, horizontal=True)
        t_amt = c2.number_input("Amount", value=default_vals["amt"])
        t_cat = c2.selectbox("Category", ["Food", "Salary", "Shopping", "Bills", "Health", "Social", "Others"], index=["Food", "Salary", "Shopping", "Bills", "Health", "Social", "Others"].index(default_vals["cat"]))
        t_note = st.text_area("Note", value=default_vals["note"])
        
        btn_label = "ပြင်ဆင်မှုကို သိမ်းမည်" if edit_mode else "Cloud ပေါ်သိမ်းမည်"
        if st.form_submit_button(btn_label):
            payload = {
                "action": "update" if edit_mode else "add",
                "index": selected_index if edit_mode else None,
                "Date": str(t_date), "Type": t_type, "Category": t_cat, "Amount": t_amt, "Note": t_note
            }
            requests.post(SCRIPT_URL, data=json.dumps(payload))
            st.success("အောင်မြင်ပါသည်။")
            st.rerun()

    if edit_mode and selected_index is not None:
        if st.button("🗑️ ဤစာရင်းကို ဖျက်ပစ်မည်", type="primary"):
            requests.post(SCRIPT_URL, data=json.dumps({"action": "delete", "index": selected_index}))
            st.rerun()

with tab2:
    st.subheader("စာရင်းမှတ်တမ်းများ")
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)

with tab3:
    st.subheader("သုံးသပ်ချက်ပုံကားချပ်များ")
    if not df.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig1 = px.pie(df[df['Type']=='Expense'], values='Amount', names='Category', title="အသုံးစရိတ် အမျိုးအစားအလိုက်")
            st.plotly_chart(fig1, use_container_width=True)
        with col_b:
            # လအလိုက် Chart
            df['Date'] = pd.to_datetime(df['Date'])
            df['Month'] = df['Date'].dt.strftime('%b %Y')
            monthly_df = df.groupby(['Month', 'Type'])['Amount'].sum().reset_index()
            fig2 = px.bar(monthly_df, x='Month', y='Amount', color='Type', barmode='group', title="လအလိုက် ဝင်ငွေ/ထွက်ငွေ")
            st.plotly_chart(fig2, use_container_width=True)
