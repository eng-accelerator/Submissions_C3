"""
Manual Financial Data Entry
Quick workaround to add financial data manually until RAG processing is configured
"""

import streamlit as st
from utils.session_state import check_authentication
from database.db_manager import DBManager
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Manual Data Entry", page_icon="✏️", layout="wide")

# Check authentication
if not check_authentication():
    st.error("Please login first!")
    st.stop()

db = DBManager()
user = db.get_user_by_id(st.session_state.user_id)

st.title("✏️ Manual Financial Data Entry")

st.info("""
**Quick Workaround:** Use this page to manually add your financial data until document processing is configured.

This will populate your Dashboard and allow AI agents to access your financial information.
""")

tab1, tab2 = st.tabs(["➕ Add Data", "📊 View/Delete Data"])

# Tab 1: Add Data
with tab1:
    st.subheader("Add Financial Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_type = st.selectbox(
            "Data Type",
            options=["Income", "Expense", "Debt", "Investment"],
            help="Select the type of financial data"
        )
    
    with col2:
        category = st.text_input(
            "Category",
            placeholder="e.g., Salary, Rent, Home Loan, Stocks",
            help="Specific category for this entry"
        )
    
    col1, col2 = st.columns(2)
    
    with col1:
        amount = st.number_input(
            "Amount (₹)",
            min_value=0.0,
            step=100.0,
            help="Enter the amount"
        )
    
    with col2:
        transaction_date = st.date_input(
            "Date",
            value=datetime.now(),
            help="Transaction or entry date"
        )
    
    description = st.text_area(
        "Description (Optional)",
        placeholder="Additional details about this entry",
        help="Optional description"
    )
    
    if st.button("➕ Add Financial Data", type="primary", use_container_width=True):
        if not category or amount <= 0:
            st.error("Please fill in category and amount")
        else:
            result = db.add_financial_data(
                user_id=st.session_state.user_id,
                data_type=data_type.lower(),
                category=category,
                amount=amount,
                description=description,
                transaction_date=datetime.combine(transaction_date, datetime.min.time())
            )
            
            if result:
                st.success(f"✅ Added {data_type}: ₹{amount:,.2f} - {category}")
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to add data")
    
    st.divider()
    
    # Quick Add Templates
    st.subheader("📝 Quick Add Templates")
    
    st.markdown("**Common Entries:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💰 Income:**")
        if st.button("Add Monthly Salary"):
            db.add_financial_data(
                user_id=st.session_state.user_id,
                data_type='income',
                category='Salary',
                amount=user.monthly_income or 50000,
                description='Monthly Salary',
                transaction_date=datetime.now()
            )
            st.success("Added salary income!")
            st.rerun()
    
    with col2:
        st.markdown("**🏠 Debts:**")
        
        with st.form("quick_loan"):
            loan_type = st.selectbox("Loan Type", ["Home Loan", "Car Loan", "Personal Loan", "Credit Card"])
            loan_amount = st.number_input("Outstanding Amount (₹)", min_value=0.0, step=10000.0)
            
            if st.form_submit_button("Add Loan"):
                if loan_amount > 0:
                    db.add_financial_data(
                        user_id=st.session_state.user_id,
                        data_type='debt',
                        category=loan_type,
                        amount=loan_amount,
                        description=f'Outstanding {loan_type}',
                        transaction_date=datetime.now()
                    )
                    st.success(f"Added {loan_type}!")
                    st.rerun()

# Tab 2: View/Delete Data
with tab2:
    st.subheader("📊 Your Financial Data")
    
    all_data = db.get_financial_data(st.session_state.user_id)
    
    if all_data:
        # Summary
        col1, col2, col3, col4 = st.columns(4)
        
        income = [d for d in all_data if d.data_type == 'income']
        expenses = [d for d in all_data if d.data_type == 'expense']
        debts = [d for d in all_data if d.data_type == 'debt']
        investments = [d for d in all_data if d.data_type == 'investment']
        
        with col1:
            st.metric("💰 Income", f"₹{sum(d.amount for d in income):,.0f}")
        with col2:
            st.metric("💸 Expenses", f"₹{sum(d.amount for d in expenses):,.0f}")
        with col3:
            st.metric("💳 Debts", f"₹{sum(d.amount for d in debts):,.0f}")
        with col4:
            st.metric("📈 Investments", f"₹{sum(d.amount for d in investments):,.0f}")
        
        st.divider()
        
        # Filter
        filter_type = st.selectbox(
            "Filter by Type",
            options=["All", "Income", "Expense", "Debt", "Investment"]
        )
        
        filtered_data = all_data if filter_type == "All" else [d for d in all_data if d.data_type == filter_type.lower()]
        
        # Display data
        for data in sorted(filtered_data, key=lambda x: x.created_at, reverse=True):
            with st.expander(f"{data.data_type.upper()}: ₹{data.amount:,.2f} - {data.category}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Type:** {data.data_type.title()}")
                    st.write(f"**Category:** {data.category}")
                    st.write(f"**Amount:** ₹{data.amount:,.2f}")
                    st.write(f"**Date:** {data.transaction_date.strftime('%Y-%m-%d') if data.transaction_date else 'N/A'}")
                    st.write(f"**Description:** {data.description or 'N/A'}")
                
                with col2:
                    if st.button("🗑️ Delete", key=f"del_{data.id}"):
                        from database.models import SessionLocal
                        session = SessionLocal()
                        try:
                            from database.models import FinancialData as FD
                            session.query(FD).filter(FD.id == data.id).delete()
                            session.commit()
                            st.success("Deleted!")
                            st.rerun()
                        except:
                            session.rollback()
                        finally:
                            session.close()
    else:
        st.info("No financial data yet. Add some data using the 'Add Data' tab above.")

st.divider()

st.markdown("""
### 💡 Tips:

1. **Add your debts**: Home loan, car loan, credit card balances
2. **Add regular expenses**: Rent, utilities, groceries, etc.
3. **Add investments**: Mutual funds, stocks, FD, PPF
4. **Keep it updated**: Add new transactions regularly

Once you have data here:
- ✅ Dashboard will show charts and metrics
- ✅ AI agents can provide personalized advice
- ✅ Financial health score will be calculated
""")
