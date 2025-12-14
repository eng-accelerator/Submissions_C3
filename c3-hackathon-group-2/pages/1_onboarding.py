"""
Onboarding Page - Data Collection
Part of multi-page app with sidebar enabled.
"""
import streamlit as st

# Page config
st.set_page_config(
    page_title="Get Started - Finance Coach",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"  # Show sidebar on app pages
)

# Initialize session state for guest mode
if 'guest_data' not in st.session_state:
    st.session_state.guest_data = {
        'snapshot': {},
        'assets': [],
        'liabilities': [],
        'goals': [],
        'plan': None
    }

# Check if user is logged in
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Sidebar
with st.sidebar:
    st.title("💰 Finance AI Coach")
    st.markdown("---")
    st.markdown("### 📍 Pages")
    
    # Current page indicator
    st.button("📝 Get Started", use_container_width=True, disabled=True, key="current_page")
    
    if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
        st.switch_page("pages/2_dashboard.py")
    
    if st.button("🎯 Goals", use_container_width=True, key="nav_goals"):
        st.switch_page("pages/3_goals.py")

# Main content
st.title("📝 Let's Analyze Your Finances")
st.markdown("Answer a few quick questions to get your personalized financial analysis.")

# Financial Snapshot
st.markdown("### Step 1: Financial Snapshot")

with st.form("snapshot_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_income = st.number_input(
            "💵 Monthly Income (₹)",
            min_value=0.0,
            value=float(st.session_state.guest_data['snapshot'].get('monthly_income', 0.0)),
            step=1000.0,
            help="Your total monthly income (salary, business income, etc.)"
        )
        
        monthly_expenses = st.number_input(
            "💸 Monthly Expenses (₹)",
            min_value=0.0,
            value=float(st.session_state.guest_data['snapshot'].get('monthly_expenses', 0.0)),
            step=1000.0,
            help="Your total monthly spending (rent, bills, groceries, etc.)"
        )
    
    with col2:
        # Calculate and show monthly surplus
        monthly_surplus = monthly_income - monthly_expenses
        
        st.markdown("#### 💡 Calculated")
        st.metric(
            "Monthly Surplus",
            f"₹{monthly_surplus:,.0f}",
            delta="Available for savings/goals" if monthly_surplus > 0 else "Budget deficit",
            delta_color="normal" if monthly_surplus >= 0 else "inverse"
        )
        
        st.markdown("")
        existing_savings = st.number_input(
            "💰 Existing Savings Balance (₹)",
            min_value=0.0,
            value=float(st.session_state.guest_data['snapshot'].get('current_savings', 0.0)),
            step=5000.0,
            help="Total money you already have saved (bank accounts, FDs, liquid funds)"
        )
    
    submitted = st.form_submit_button("➡️ Next: Add Assets & Debts", use_container_width=True, type="primary")
    
    if submitted:
        if monthly_income == 0:
            st.error("Please enter your monthly income")
        else:
            st.session_state.guest_data['snapshot'] = {
                'monthly_income': monthly_income,
                'monthly_expenses': monthly_expenses,
                'current_savings': existing_savings,
            }
            
            # Save to database if logged in or guest
            if st.session_state.get("user"):
                from services.auth_service import AuthService
                AuthService.save_guest_data(st.session_state.user["user_id"], st.session_state.guest_data)
            
            st.success("✅ Snapshot saved!")
            st.session_state.onboarding_step = 2
            st.rerun()

# Assets & Liabilities
if st.session_state.get('onboarding_step', 1) >= 2:
    st.markdown("---")
    st.markdown("### Step 2: Assets & Debts")
    
    tab1, tab2 = st.tabs(["💰 Assets", "💳 Debts"])
    
    with tab1:
        st.markdown("Add your investments and assets")
        
        with st.form("asset_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                asset_type = st.selectbox("Type", ["Cash", "Fixed Deposit", "Mutual Fund", "Stocks", "Gold", "Other"])
            with col2:
                asset_name = st.text_input("Name", placeholder="e.g., HDFC Equity Fund")
            with col3:
                asset_value = st.number_input("Value (₹)", min_value=0, step=1000)
            
            if st.form_submit_button("➕ Add Asset"):
                if asset_name and asset_value > 0:
                    st.session_state.guest_data['assets'].append({
                        'type': asset_type.lower().replace(' ', '_'),
                        'name': asset_name,
                        'value': asset_value
                    })
                    st.success(f"✅ Added {asset_name}")
                    st.rerun()
        
        # Show existing assets
        if st.session_state.guest_data['assets']:
            st.markdown("**Your Assets:**")
            for idx, asset in enumerate(st.session_state.guest_data['assets']):
                col1, col2, col3 = st.columns([3, 2, 1])
                col1.write(f"**{asset['name']}** ({asset['type']})")
                col2.write(f"₹{asset['value']:,.0f}")
                if col3.button("🗑️", key=f"del_asset_{idx}"):
                    st.session_state.guest_data['assets'].pop(idx)
                    st.rerun()
    
    with tab2:
        st.markdown("Add your loans and credit card debt")
        
        with st.form("liability_form"):
            col1, col2 = st.columns(2)
            with col1:
                debt_type = st.selectbox("Type", ["Credit Card", "Personal Loan", "Home Loan", "Car Loan", "Other"])
                debt_name = st.text_input("Name", placeholder="e.g., HDFC Credit Card")
            with col2:
                outstanding = st.number_input("Outstanding (₹)", min_value=0, step=1000)
                interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, max_value=100.0, value=12.0)
            
            if st.form_submit_button("➕ Add Debt"):
                if debt_name and outstanding > 0:
                    st.session_state.guest_data['liabilities'].append({
                        'type': debt_type.lower().replace(' ', '_'),
                        'name': debt_name,
                        'outstanding': outstanding,
                        'interest_rate': interest_rate / 100
                    })
                    st.success(f"✅ Added {debt_name}")
                    st.rerun()
        
        # Show existing debts
        if st.session_state.guest_data['liabilities']:
            st.markdown("**Your Debts:**")
            for idx, debt in enumerate(st.session_state.guest_data['liabilities']):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                col1.write(f"**{debt['name']}**")
                col2.write(f"₹{debt['outstanding']:,.0f}")
                col3.write(f"{debt['interest_rate']*100:.1f}% APR")
                if col4.button("🗑️", key=f"del_debt_{idx}"):
                    st.session_state.guest_data['liabilities'].pop(idx)
                    st.rerun()
    
    # Generate analysis button
    st.markdown("---")
    if st.button("📊 Generate My Financial Analysis", use_container_width=True, type="primary"):
        # Import calculator service
        from services.calculator import FinancialCalculator
        
        # Run analysis
        analysis = FinancialCalculator.analyze_financial_health(
            st.session_state.guest_data['snapshot'],
            st.session_state.guest_data['assets'],
            st.session_state.guest_data['liabilities']
        )
        
        st.session_state.guest_data['analysis'] = analysis
        
        # Save to database if logged in or guest
        if st.session_state.get("user"):
            from services.auth_service import AuthService
            AuthService.save_guest_data(st.session_state.user["user_id"], st.session_state.guest_data)
            
        st.success("✅ Analysis complete!")
        if st.session_state.get("user"):
            st.info("💾 Data saved to your account!")
        st.balloons()
        
        # Navigate to dashboard
        st.switch_page("pages/2_dashboard.py")
