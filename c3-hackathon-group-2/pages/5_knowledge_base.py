import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(page_title="Knowledge Base", page_icon="📚", layout="wide")

# Sidebar
with st.sidebar:
    st.title("💰 Personal Finance Coach")
    st.markdown("---")
# ... (rest of sidebar code is unchanged, usually I'd skip it but the replace block needs context or precise targeting)
# Actually, I can target just the import area and the specific block for st.status.

# Let's do huge replacement or precise chunks.
# The user's file is relatively small. I will target the imports first.

with st.sidebar:
    st.title("💰 Personal Finance Coach")
    st.markdown("---")
    st.markdown("### 📍 Pages")
    
    if st.button("📝 Get Started", use_container_width=True, key="nav_onboard"):
        st.switch_page("pages/1_onboarding.py")
    
    if st.button("📊 Dashboard", use_container_width=True, key="nav_dash"):
        st.switch_page("pages/2_dashboard.py")
    
    if st.button("🎯 Goals", use_container_width=True, key="nav_goals"):
        st.switch_page("pages/3_goals.py")
        
    # Current page
    st.button("📚 Knowledge Base", use_container_width=True, disabled=True, key="current_page")

# Main content
st.title("📚 Financial Knowledge Base")
st.markdown("Upload your financial documents (statements, reports, guides) and ask questions about them.")

# Initialize session state for chat
if "rag_chat_history" not in st.session_state:
    st.session_state.rag_chat_history = []

if "uploaded_docs" not in st.session_state:
    st.session_state.uploaded_docs = []

# Layout: Document Management in Expander, Chat in Main Area
with st.expander("📂 Document Management", expanded=not st.session_state.uploaded_docs):
    # API Key Check
    if not os.getenv("OPENROUTER_API_KEY") or not os.getenv("HUGGINGFACE_API_KEY"):
        st.warning("⚠️ API Keys Missing! Please add OPENROUTER_API_KEY and HUGGINGFACE_API_KEY to your .env file.")
    
    col_upload, col_list = st.columns([1, 2])
    
    with col_upload:
        uploaded_files = st.file_uploader(
            "Upload Documents", 
            type=["pdf", "txt", "csv", "xlsx", "xls"], 
            accept_multiple_files=True,
            help="Supported formats: PDF, Text, CSV, Excel"
        )
        
        if uploaded_files:
            if st.button(f"📥 Process {len(uploaded_files)} Files", type="primary", use_container_width=True):
                with st.spinner("Processing documents..."):
                    st.write("Initializing RAG service...")
                    try:
                        from services.rag_service import rag_service
                        
                        for file in uploaded_files:
                            st.write(f"Processing {file.name}...")
                            file_path = os.path.join(rag_service.UPLOAD_DIR, file.name)
                            success = rag_service.process_file(file.getvalue(), file.name)
                            
                            if success:
                                st.write(f"✅ Indexed {file.name}")
                                if file.name not in st.session_state.uploaded_docs:
                                    st.session_state.uploaded_docs.append(file.name)
                                
                                # Auto-Extract Data
                                st.write(f"🔍 Analyzing {file.name} for financial data...")
                                try:
                                    # Need full path for extraction
                                    data = rag_service.extract_financial_data(file_path)
                                    if data:
                                        # Merge Snapshot (Overwrite if non-zero)
                                        snap = data.get('snapshot', {})
                                        if snap.get('monthly_income', 0) > 0:
                                            st.session_state.guest_data['snapshot']['monthly_income'] = snap['monthly_income']
                                        if snap.get('monthly_expenses', 0) > 0:
                                            st.session_state.guest_data['snapshot']['monthly_expenses'] = snap['monthly_expenses']
                                        if snap.get('current_savings', 0) > 0:
                                            st.session_state.guest_data['snapshot']['current_savings'] = snap['current_savings']
                                            
                                        # Extend Arrays
                                        if data.get('assets'):
                                            st.session_state.guest_data['assets'].extend(data['assets'])
                                        if data.get('liabilities'):
                                            st.session_state.guest_data['liabilities'].extend(data['liabilities'])
                                            
                                        st.success(f"📊 Updated dashboard with data from {file.name}")
                                except Exception as e:
                                    print(f"Extraction failed: {e}")
                                    
                            else:
                                st.error(f"❌ Failed to process {file.name}")
                        
                        # Save changes
                        if st.session_state.get("user"):
                            from services.auth_service import AuthService
                            AuthService.save_guest_data(st.session_state.user["user_id"], st.session_state.guest_data)
                            st.toast("Dashboard updated & saved!", icon="💾")
                        
                        st.success("✅ Documents Processed!")
                        st.session_state.rag_chat_history.append({"role": "assistant", "content": "I've processed your documents and updated your dashboard with any financial data I found. You can now ask me questions about them!"})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to initialize RAG service: {str(e)}")

    with col_list:
        if st.session_state.uploaded_docs:
            st.markdown("### 📑 Indexed Documents")
            # Deduplicate and show
            for doc in set(st.session_state.uploaded_docs):
                st.caption(f"📄 {doc}")
        else:
            st.info("No documents indexed yet. Upload files to analyze them.")

st.markdown("---")
st.subheader("🤖 AI Financial Assistant")

# Chat Interface
# Display chat history
for message in st.session_state.rag_chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if not st.session_state.rag_chat_history:
    st.info("👋 Upload documents above, then ask me anything about them!")

# Chat Input (Must be in main body)
if prompt := st.chat_input("Ask a question about your documents..."):
    # Add user message
    st.session_state.rag_chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                from services.rag_service import rag_service
                response = rag_service.query(prompt)
            except Exception as e:
                response = f"⚠️ Error: {str(e)}\n\nPlease ensure OPENROUTER_API_KEY is set in your .env file."
            
            st.markdown(response)
            
    st.session_state.rag_chat_history.append({"role": "assistant", "content": response})
