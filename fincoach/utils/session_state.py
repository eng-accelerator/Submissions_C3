import streamlit as st

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    
    if 'username' not in st.session_state:
        st.session_state.username = None
    
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

def logout():
    """Clear session state and logout"""
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.user_data = None
    st.session_state.page = 'login'

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)

def get_user_id():
    """Get current user ID"""
    return st.session_state.get('user_id')

def get_username():
    """Get current username"""
    return st.session_state.get('username')
