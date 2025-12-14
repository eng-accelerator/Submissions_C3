import streamlit as st
from utils.session_state import check_authentication
from database.db_manager import DBManager
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# Check authentication
if not check_authentication():
    st.error("Please login first!")
    st.stop()

db = DBManager()
user = db.get_user_by_id(st.session_state.user_id)

st.title("📊 Financial Dashboard")

# Get financial data - get ALL data first
all_data = db.get_financial_data(user.id)

# Separate by type with proper filtering
expenses = [d for d in all_data if d.data_type == 'expense' and d.amount and 0 < d.amount < 1e10]
income_data = [d for d in all_data if d.data_type == 'income' and d.amount and 0 < d.amount < 1e10]
debts = [d for d in all_data if d.data_type == 'debt' and d.amount and 0 < d.amount < 1e10]
investments = [d for d in all_data if d.data_type == 'investment' and d.amount and 0 < d.amount < 1e10]

# Calculate totals
total_expenses = sum(e.amount for e in expenses)
total_income = sum(i.amount for i in income_data)

# Use profile monthly income if no income data
if total_income == 0 and user.monthly_income:
    total_income = user.monthly_income

total_debt = sum(d.amount for d in debts)
total_investments = sum(inv.amount for inv in investments)

# Calculate metrics
savings = total_income - total_expenses
savings_rate = (savings / total_income * 100) if total_income > 0 else 100
debt_to_income = (total_debt / (total_income * 12)) if total_income > 0 else 0

# Top metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Monthly Income",
        value=f"₹{total_income:,.0f}",
        delta="Stable" if total_income > 0 else None
    )

with col2:
    st.metric(
        label="Total Expenses",
        value=f"₹{total_expenses:,.0f}",
        delta=f"-{(total_expenses/total_income*100):.1f}%" if total_income > 0 and total_expenses > 0 else None,
        delta_color="inverse"
    )

with col3:
    st.metric(
        label="Total Debt",
        value=f"₹{total_debt:,.0f}",
        delta=f"{debt_to_income:.1f}x income" if debt_to_income > 0 else "Debt-free!",
        delta_color="inverse" if total_debt > 0 else "normal"
    )

with col4:
    st.metric(
        label="Savings Rate",
        value=f"{savings_rate:.1f}%",
        delta="Healthy" if savings_rate > 20 else "Improve",
        delta_color="normal" if savings_rate > 20 else "inverse"
    )

st.divider()

# Charts Row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("💰 Income vs Expenses")
    
    # Create simple bar chart
    chart_data = pd.DataFrame({
        'Category': ['Income', 'Expenses', 'Savings'],
        'Amount': [total_income, total_expenses, savings]
    })
    
    fig1 = px.bar(
        chart_data,
        x='Category',
        y='Amount',
        color='Category',
        color_discrete_map={
            'Income': '#2ecc71',
            'Expenses': '#e74c3c',
            'Savings': '#3498db'
        }
    )
    fig1.update_layout(
        height=350,
        showlegend=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📊 Expense Breakdown")
    
    # Get expense categories
    expense_categories = {}
    for expense in expenses:
        cat = expense.category or 'Other'
        expense_categories[cat] = expense_categories.get(cat, 0) + expense.amount
    
    if expense_categories:
        fig2 = px.pie(
            values=list(expense_categories.values()),
            names=list(expense_categories.keys()),
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig2.update_traces(textposition='inside', textinfo='percent+label')
        fig2.update_layout(height=350, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("📭 No expense data available yet. Upload documents to see your spending patterns.")

st.divider()

# Recent transactions
st.subheader("🔄 Recent Financial Activities")

if all_data:
    # Sort by date
    sorted_data = sorted(
        [d for d in all_data if d.amount and 0 < d.amount < 1e10],
        key=lambda x: x.transaction_date or x.created_at or datetime.now(),
        reverse=True
    )[:15]
    
    df_transactions = pd.DataFrame([
        {
            'Date': (d.transaction_date or d.created_at).strftime('%Y-%m-%d') if (d.transaction_date or d.created_at) else 'N/A',
            'Type': d.data_type.title(),
            'Category': d.category or 'N/A',
            'Amount': f"₹{d.amount:,.2f}",
            'Description': (d.description[:50] + '...' if d.description and len(d.description) > 50 else d.description) or 'N/A'
        }
        for d in sorted_data
    ])
    st.dataframe(df_transactions, use_container_width=True, hide_index=True)
else:
    st.info("📭 No transaction data. Add data via 'Manual Data Entry' page.")

st.divider()

# Financial health score
st.subheader("🎯 Financial Health Score")

# Calculate health score
health_score = 0
score_components = {}

# Income factor (20 points)
if total_income > 0:
    health_score += 20
    score_components['Income Source'] = 20
else:
    score_components['Income Source'] = 0

# Savings rate (25 points)
if savings_rate > 30:
    health_score += 25
    score_components['Savings Rate'] = 25
elif savings_rate > 20:
    health_score += 20
    score_components['Savings Rate'] = 20
elif savings_rate > 10:
    health_score += 15
    score_components['Savings Rate'] = 15
else:
    score_components['Savings Rate'] = 10
    health_score += 10

# Debt management (25 points)
if total_debt == 0:
    health_score += 25
    score_components['Debt Management'] = 25
elif debt_to_income < 0.3:
    health_score += 20
    score_components['Debt Management'] = 20
elif debt_to_income < 0.5:
    health_score += 15
    score_components['Debt Management'] = 15
else:
    score_components['Debt Management'] = 5
    health_score += 5

# Investment (20 points) - FIXED: Now checks for investments properly
if total_investments > total_income * 6:
    health_score += 20
    score_components['Investments'] = 20
elif total_investments > total_income * 3:
    health_score += 15
    score_components['Investments'] = 15
elif total_investments > 0:
    health_score += 10
    score_components['Investments'] = 10
else:
    score_components['Investments'] = 0

# Documents (10 points)
docs_score = sum([
    user.has_salary_slip,
    user.has_bank_statement,
    user.has_loan_data,
    user.has_credit_card_statement,
    user.has_collateral_details
]) * 2
health_score += docs_score
score_components['Profile Completion'] = docs_score

col1, col2 = st.columns([2, 1])

with col1:
    # Score gauge
    if health_score >= 80:
        score_color = "#2ecc71"
        score_text = "Excellent"
        score_emoji = "🌟"
    elif health_score >= 60:
        score_color = "#f39c12"
        score_text = "Good"
        score_emoji = "👍"
    else:
        score_color = "#e74c3c"
        score_text = "Needs Improvement"
        score_emoji = "⚠️"
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=health_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"{score_emoji} Financial Health"},
        delta={'reference': 70},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': score_color},
            'steps': [
                {'range': [0, 40], 'color': "#ffebee"},
                {'range': [40, 70], 'color': "#fff9e6"},
                {'range': [70, 100], 'color': "#e8f5e9"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    fig_gauge.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.markdown(f"### {score_text}")
    st.markdown("#### Score Breakdown")
    for component, score in score_components.items():
        if component == 'Profile Completion':
            max_score = 10
        else:
            max_score = 25 if component != 'Income Source' else 20
        st.progress(score / max_score, text=f"{component}: {score}/{max_score}")

st.divider()

# Quick Actions - FIXED BUTTONS
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("💬 Ask AI Coach", use_container_width=True, type="primary", key="btn_chat"):
        st.switch_page("pages/3_💬_Chat.py")

with col2:
    if st.button("📄 Upload Documents", use_container_width=True, key="btn_upload"):
        st.switch_page("pages/2_👤_Profile.py")

with col3:
    if st.button("✏️ Add Data Manually", use_container_width=True, key="btn_manual"):
        if "4_✏️_Manual_Data_Entry.py" in [f for f in st.session_state.get('pages', [])]:
            st.switch_page("pages/4_✏️_Manual_Data_Entry.py")
        else:
            st.warning("Manual Data Entry page not found. Please add 4___Manual_Data_Entry.py to pages folder.")

with col4:
    if st.button("🗑️ Manage Data", use_container_width=True, key="btn_manage"):
        st.switch_page("pages/2_👤_Profile.py")