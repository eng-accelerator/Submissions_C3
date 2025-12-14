import streamlit as st
from auth.auth_manager import AuthManager
from utils.session_state import init_session_state, check_authentication, logout
from database.models import init_db
from database.db_manager import DBManager
import os

# Page configuration
st.set_page_config(
    page_title="AI Financial Coach",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()

# Initialize database (first time setup)
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        text-align: center;
        color: #555;
        margin-bottom: 3rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

def show_login_page():
    """Display login page"""
    st.markdown('<div class="main-header">💰 AI Financial Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your Personal Financial Advisor Powered by AI</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    # Login Tab
    with tab1:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("Welcome Back!")
        
        with st.form("login_form"):
            username_or_email = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("Login")
            with col2:
                forgot_password = st.form_submit_button("Forgot Password?")
            
            if submit:
                if not username_or_email or not password:
                    st.error("Please fill in all fields")
                else:
                    auth = AuthManager()
                    success, message, user_id = auth.login_user(username_or_email, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user_id = user_id
                        user = auth.get_user_info(user_id)
                        st.session_state.username = user.username
                        st.session_state.user_data = user
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            
            if forgot_password:
                st.info("Password reset feature coming soon!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Register Tab
    with tab2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name", placeholder="John Doe")
                username = st.text_input("Username*", placeholder="johndoe")
                email = st.text_input("Email*", placeholder="john@example.com")
            
            with col2:
                phone = st.text_input("Phone Number", placeholder="+91 98765 43210")
                password = st.text_input("Password*", type="password", placeholder="Min 8 chars")
                confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter password")
            
            st.markdown("**Password Requirements:**")
            st.markdown("- At least 8 characters\n- One uppercase letter\n- One lowercase letter\n- One digit")
            
            agree = st.checkbox("I agree to the Terms and Conditions")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all required fields (*)")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif not agree:
                    st.error("Please agree to the Terms and Conditions")
                else:
                    auth = AuthManager()
                    success, message = auth.register_user(
                        username=username,
                        email=email,
                        password=password,
                        full_name=full_name,
                        phone=phone
                    )
                    
                    if success:
                        st.success(f"{message} Please login to continue.")
                    else:
                        st.error(message)
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_main_dashboard():
    """Display main dashboard after login"""
    db = DBManager()
    user = db.get_user_by_id(st.session_state.user_id)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150", width=150)
        st.title(f"Welcome, {user.full_name or user.username}!")
        st.write(f"📧 {user.email}")
        st.write(f"📱 {user.phone or 'Not provided'}")
        
        st.divider()
        
        st.subheader("🎯 Quick Actions")
        if st.button("💬 Chat with AI Coach"):
            st.info("Chat feature coming in next step!")
        if st.button("📊 View Analytics"):
            st.info("Analytics coming soon!")
        if st.button("📄 Upload Documents"):
            st.info("Document upload coming in next step!")
        
        st.divider()
        
        if st.button("🚪 Logout"):
            logout()
            st.rerun()
    
    # Main content
    st.title("💰 AI Financial Coach Dashboard")
    
    # Profile completion status
    st.subheader("📋 Profile Completion Status")
    
    completion_items = {
        "Personal Information": user.full_name and user.phone and user.age,
        "Salary Slip": user.has_salary_slip,
        "Bank Statement (3 months)": user.has_bank_statement,
        "Loan Data": user.has_loan_data,
        "Credit Card Statement": user.has_credit_card_statement,
        "Collateral Details": user.has_collateral_details
    }
    
    completed = sum(1 for v in completion_items.values() if v)
    total = len(completion_items)
    completion_percentage = (completed / total) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Profile Completion", f"{completion_percentage:.0f}%")
    with col2:
        st.metric("Documents Uploaded", completed)
    with col3:
        st.metric("Monthly Income", f"₹{user.monthly_income:,.0f}" if user.monthly_income else "Not Set")
    with col4:
        st.metric("Account Status", "✅ Active" if user.is_active else "❌ Inactive")
    
    st.progress(completion_percentage / 100)
    
    # Checklist
    st.subheader("✅ Required Documents Checklist")
    
    col1, col2 = st.columns(2)
    with col1:
        for item, status in list(completion_items.items())[:3]:
            if status:
                st.success(f"✅ {item}")
            else:
                st.warning(f"⏳ {item}")
    
    with col2:
        for item, status in list(completion_items.items())[3:]:
            if status:
                st.success(f"✅ {item}")
            else:
                st.warning(f"⏳ {item}")
    
    # Welcome message and instructions
    st.divider()
    st.subheader("🎯 Get Started with AI Financial Coach")
    
    st.info("""
    **Welcome to your AI Financial Coach!** 
    
    To get the most personalized financial advice, please:
    1. Complete your profile information
    2. Upload required financial documents
    3. Start chatting with our AI agents for personalized advice
    
    Our AI agents can help you with:
    - 📊 Debt Analysis & Payoff Plans
    - 💰 Custom Savings Strategies
    - 📈 Investment Portfolio Building
    - 🏠 Retirement Planning
    - 💳 Budget Optimization
    """)
    
    # Feature cards
    st.divider()
    st.subheader("🚀 Available Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 AI Agents
        - Debt Analyzer
        - Savings Strategist
        - Investment Advisor
        - Budget Planner
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Analytics
        - Spending Patterns
        - Income Trends
        - Debt Overview
        - Investment Growth
        """)
    
    with col3:
        st.markdown("""
        ### 📄 Documents
        - Salary Slips
        - Bank Statements
        - Loan Documents
        - Tax Records
        """)

# Main app logic
if check_authentication():
    show_main_dashboard()
else:
    show_login_page()
