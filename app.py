import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from datetime import date

# 1. UI Configuration
st.set_page_config(page_title="Pro Finance Manager", layout="wide")

# 2. Connection Setup
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(worksheet="MyFinanceData", ttl="5s")
        data.columns = [c.strip() for c in data.columns]
        return data
    except:
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Note"])

df = load_data()

# 3. Sidebar - Settings & Features
st.sidebar.title("⚙️ Settings")
lang = st.sidebar.selectbox("Language", ["Myanmar", "English"])
monthly_budget = st.sidebar.number_input("Monthly Budget (Limit)", min_value=0, value=500000)

L = {
    "title": "ငွေစာရင်း စီမံခန့်ခွဲမှု" if lang == "Myanmar" else "Pro Finance Manager",
    "add": "စာရင်းအသစ်သွင်းရန်" if lang == "Myanmar" else "Add Transaction",
    "save": "Cloud ပေါ်သိမ်းမည်" if lang == "Myanmar" else "Save to Cloud",
    "history": "မှတ်တမ်းများ" if lang == "Myanmar" else "History",
    "summary": "ခြုံငုံသုံးသပ်ချက်" if lang == "Myanmar" else "Summary"
}

st.title(f"📊 {L['title']}")

# 4. Input Form
with st.expander(f"➕ {L['add']}", expanded=False):
    with st.form("entry_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t_date = st.date_input("Date", date.today())
            t_type = st.radio("Type", ["Income", "Expense"], horizontal=True)
            t_amt = st.number_input("Amount", min_value=0.0, step=1000.0)
        with c2:
            t_cat = st.selectbox("Category", ["Food", "Salary", "Shopping", "Bills", "Travel", "Health", "Social", "Gift", "Others"])
            t_note = st.text_area("Note (မှတ်ချက်)")
        
        if st.form_submit_button(L['save']):
            if t_amt > 0:
                new_row = pd.DataFrame([{"Date": str(t_date), "Type": t_type, "Category": t_cat, "Amount": t_amt, "Note": t_note}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="MyFinanceData", data=updated_df)
                st.success("Successfully Saved!")
                st.rerun()

# 5. Dashboard & Analytics
if not df.empty:
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    inc = df[df['Type'] == 'Income']['Amount'].sum()
    exp = df[df['Type'] == 'Expense']['Amount'].sum()
    balance = inc - exp

    # Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("Current Balance", f"{balance:,.0f} MMK")
    m2.metric("Total Income", f"{inc:,.0f}")
    m3.metric("Total Expense", f"-{exp:,.0f}")

    # Budget Warning
    if exp > monthly_budget:
        st.sidebar.error(f"⚠️ Budget Over: {exp-monthly_budget:,.0f} MMK ကျော်နေပြီ!")
    else:
        st.sidebar.success(f"✅ Budget OK: {monthly_budget-exp:,.0f} MMK ကျန်သေးတယ်")

    # Visuals
    tab1, tab2 = st.tabs([L['history'], "Analysis (ပုံပြကားချပ်)"])
    with tab1:
        # Search & Filter
        search = st.text_input("🔍 Search History (Note/Category)")
        filtered_df = df[df.apply(lambda row: search.lower() in str(row).lower(), axis=1)]
        st.dataframe(filtered_df.sort_index(ascending=False), use_container_width=True)
    
    with tab2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("Expense by Category")
            exp_df = df[df['Type'] == 'Expense']
            if not exp_df.empty:
                fig_pie = px.pie(exp_df, values='Amount', names='Category', hole=0.3)
                st.plotly_chart(fig_pie, use_container_width=True)
        with col_b:
            st.write("Income vs Expense")
            fig_bar = px.bar(df, x='Type', y='Amount', color='Type', barmode='group')
            st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No data yet. စာရင်းစတင်သွင်းနိုင်ပါပြီ။")
