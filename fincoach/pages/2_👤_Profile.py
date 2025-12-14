import streamlit as st
from utils.session_state import check_authentication
from database.db_manager import DBManager
from database.models import SessionLocal, Document, FinancialData, ChatHistory, User
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Profile", page_icon="👤", layout="wide")

# Check authentication
if not check_authentication():
    st.error("Please login first!")
    st.stop()

db = DBManager()
user = db.get_user_by_id(st.session_state.user_id)

st.title("👤 User Profile & Documents")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📋 Profile Information", "📄 Document Upload", "📊 Document History", "🗑️ Data Management"])

# Tab 1: Profile Information
with tab1:
    st.subheader("Personal Information")
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=user.full_name or "")
            email = st.text_input("Email", value=user.email, disabled=True)
            phone = st.text_input("Phone Number", value=user.phone or "")
            age = st.number_input("Age", min_value=18, max_value=100, value=user.age or 30)
        
        with col2:
            occupation = st.text_input("Occupation", value=user.occupation or "")
            city = st.text_input("City", value=user.city or "")
            dependents = st.number_input("Number of Dependents", min_value=0, max_value=10, 
                                        value=user.dependents or 0)
            monthly_income = st.number_input("Monthly Income (₹)", min_value=0.0, 
                                            value=float(user.monthly_income or 0), step=1000.0)
        
        submit_profile = st.form_submit_button("💾 Update Profile", use_container_width=True)
        
        if submit_profile:
            success = db.update_user_profile(
                user_id=st.session_state.user_id,
                full_name=full_name,
                phone=phone,
                age=age,
                occupation=occupation,
                city=city,
                dependents=dependents,
                monthly_income=monthly_income
            )
            
            if success:
                st.success("✅ Profile updated successfully!")
                st.rerun()
            else:
                st.error("❌ Failed to update profile. Please try again.")
    
    st.divider()
    
    # Account Information
    st.subheader("Account Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Username", user.username)
    with col2:
        st.metric("Member Since", user.created_at.strftime('%B %Y') if user.created_at else "N/A")
    with col3:
        st.metric("Last Login", user.last_login.strftime('%Y-%m-%d %H:%M') if user.last_login else "Never")

# Tab 2: Document Upload
with tab2:
    st.subheader("📤 Upload Financial Documents")
    
    st.info("""
    Upload your financial documents to get personalized AI-powered insights. 
    Documents will be processed to extract financial data automatically.
    """)
    
    # Document type selection
    document_types = {
        "💼 Salary Slip / Income Statement": "salary_slip",
        "🏦 Bank Statement (Last 3 Months)": "bank_statement",
        "💳 Credit Card Statement": "credit_card_statement",
        "🏠 Loan Documents": "loan_data",
        "📊 Collateral Details (Assets)": "collateral_details",
        "📈 Investment Statements": "investment_statement",
        "🧾 Tax Documents": "tax_documents"
    }
    
    selected_doc_type = st.selectbox(
        "Select Document Type",
        options=list(document_types.keys())
    )
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['pdf', 'csv', 'xlsx', 'xls', 'jpg', 'jpeg', 'png'],
        help="Supported formats: PDF, CSV, Excel, Images"
    )
    
    if uploaded_file:
        # Display file info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
        with col3:
            st.metric("File Type", uploaded_file.type)
        
        if st.button("📤 Upload and Process Document", type="primary", use_container_width=True):
            with st.spinner("📊 Processing document... This may take a minute."):
                try:
                    # Create uploads directory if not exists
                    upload_dir = "uploads"
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save uploaded file
                    file_path = os.path.join(upload_dir, f"{st.session_state.user_id}_{uploaded_file.name}")
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Try to process with RAG system
                    try:
                        from processors.rag_system import RAGSystem
                        rag = RAGSystem(db_manager=db)
                        
                        result = rag.process_uploaded_document(
                            user_id=st.session_state.user_id,
                            file_path=file_path,
                            document_type=document_types[selected_doc_type],
                            file_name=uploaded_file.name
                        )
                        
                        if result['success']:
                            st.success(f"""
                            ✅ **Document Processed Successfully!**
                            
                            - Document ID: {result.get('document_id')}
                            - Text Chunks: {result.get('chunks_created', 0)}
                            - Vectors Created: {result.get('vectors_created', 0)}
                            
                            {result.get('message', '')}
                            """)
                            
                            # Show extracted financial data if available
                            session = SessionLocal()
                            try:
                                financial_data = session.query(FinancialData).filter(
                                    FinancialData.user_id == st.session_state.user_id,
                                    FinancialData.source_document_id == result.get('document_id')
                                ).all()
                                
                                if financial_data:
                                    st.subheader("📊 Extracted Financial Data")
                                    df = pd.DataFrame([
                                        {
                                            'Type': d.data_type.title(),
                                            'Category': d.category or 'N/A',
                                            'Amount': f"₹{d.amount:,.2f}",
                                            'Description': d.description or 'N/A'
                                        }
                                        for d in financial_data
                                    ])
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                            finally:
                                session.close()
                            
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Document uploaded but processing had issues: {result.get('message')}")
                            st.info("Document is saved and can be reprocessed later.")
                    
                    except ImportError:
                        # RAG system not available, just save document
                        doc = db.add_document(
                            user_id=st.session_state.user_id,
                            document_type=document_types[selected_doc_type],
                            file_name=uploaded_file.name,
                            file_path=file_path,
                            metadata={'upload_date': datetime.utcnow().isoformat()}
                        )
                        
                        if doc:
                            st.success(f"""
                            ✅ **Document Uploaded!**
                            
                            - Document ID: {doc.id}
                            - Type: {selected_doc_type}
                            - File: {uploaded_file.name}
                            
                            ⚠️ **Note:** Document processing is not configured. 
                            You can manually add financial data or configure RAG system for automatic extraction.
                            """)
                        else:
                            st.error("❌ Failed to save document to database")
                    
                    st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Error uploading document: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

# Tab 3: Document History
with tab3:
    st.subheader("📚 Your Uploaded Documents")
    
    documents = db.get_user_documents(st.session_state.user_id)
    
    if documents:
        # Create summary cards
        col1, col2, col3 = st.columns(3)
        
        doc_types = {}
        for doc in documents:
            doc_types[doc.document_type] = doc_types.get(doc.document_type, 0) + 1
        
        with col1:
            st.metric("Total Documents", len(documents))
        with col2:
            st.metric("Processed", sum(1 for d in documents if d.processed))
        with col3:
            st.metric("Document Types", len(doc_types))
        
        st.divider()
        
        # Document list
        for doc in sorted(documents, key=lambda x: x.uploaded_at, reverse=True):
            with st.expander(f"📄 {doc.file_name} - {doc.document_type.replace('_', ' ').title()}"):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Document Type:** {doc.document_type.replace('_', ' ').title()}")
                    st.write(f"**Uploaded:** {doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}")
                    st.write(f"**Status:** {'✅ Processed' if doc.processed else '⏳ Pending'}")
                    st.write(f"**File Path:** {doc.file_path}")
                
                with col2:
                    # Reprocess button
                    if not doc.processed:
                        if st.button(f"🔄 Process", key=f"process_doc_{doc.id}"):
                            with st.spinner("Processing..."):
                                try:
                                    from processors.rag_system import RAGSystem
                                    rag = RAGSystem(db_manager=db)
                                    result = rag.reprocess_document(st.session_state.user_id, doc.id)
                                    if result['success']:
                                        st.success("Processed!")
                                        st.rerun()
                                    else:
                                        st.error(result.get('message'))
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                    
                    # Delete button for individual document
                    if st.button(f"🗑️ Delete", key=f"delete_doc_{doc.id}"):
                        st.session_state[f'confirm_delete_doc_{doc.id}'] = True
                    
                    if st.session_state.get(f'confirm_delete_doc_{doc.id}', False):
                        st.warning("⚠️ Confirm?")
                        col_yes, col_no = st.columns(2)
                        
                        with col_yes:
                            if st.button("Yes", key=f"yes_delete_doc_{doc.id}"):
                                # Delete file
                                if os.path.exists(doc.file_path):
                                    try:
                                        os.remove(doc.file_path)
                                    except:
                                        pass
                                
                                # Delete from database
                                session = SessionLocal()
                                try:
                                    session.query(Document).filter(Document.id == doc.id).delete()
                                    session.query(FinancialData).filter(FinancialData.source_document_id == doc.id).delete()
                                    session.commit()
                                except:
                                    session.rollback()
                                finally:
                                    session.close()
                                
                                st.success("Deleted!")
                                del st.session_state[f'confirm_delete_doc_{doc.id}']
                                st.rerun()
                        
                        with col_no:
                            if st.button("No", key=f"no_delete_doc_{doc.id}"):
                                del st.session_state[f'confirm_delete_doc_{doc.id}']
                                st.rerun()
                
                # Show related financial data
                try:
                    all_financial_data = db.get_financial_data(st.session_state.user_id)
                    financial_data = [fd for fd in all_financial_data if fd.source_document_id == doc.id]
                except Exception as e:
                    financial_data = []
                
                if financial_data:
                    st.write(f"**Extracted Data:** {len(financial_data)} records")
                    
                    df = pd.DataFrame([
                        {
                            'Type': d.data_type.title(),
                            'Category': d.category,
                            'Amount': f"₹{d.amount:,.2f}",
                            'Date': d.transaction_date.strftime('%Y-%m-%d') if d.transaction_date else 'N/A'
                        }
                        for d in financial_data[:5]
                    ])
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    if len(financial_data) > 5:
                        st.caption(f"Showing 5 of {len(financial_data)} records")
                else:
                    st.info("No financial data extracted yet. Try reprocessing this document.")
    else:
        st.info("📭 No documents uploaded yet. Upload your first document to get started!")

# Tab 4: Data Management
with tab4:
    st.subheader("🗑️ Data Management")
    
    st.warning("""
    ⚠️ **Danger Zone**
    
    This section allows you to delete all your data and start fresh. This action cannot be undone!
    """)
    
    # Show current data statistics
    col1, col2, col3 = st.columns(3)
    
    documents = db.get_user_documents(st.session_state.user_id)
    session = SessionLocal()
    try:
        financial_count = session.query(FinancialData).filter(FinancialData.user_id == st.session_state.user_id).count()
        chat_count = session.query(ChatHistory).filter(ChatHistory.user_id == st.session_state.user_id).count()
    except Exception as e:
        financial_count = 0
        chat_count = 0
    finally:
        session.close()
    
    with col1:
        st.metric("📄 Documents", len(documents))
    with col2:
        st.metric("💰 Financial Records", financial_count)
    with col3:
        st.metric("💬 Chat Messages", chat_count)
    
    st.divider()
    
    # Delete all data option
    st.markdown("### 🗑️ Delete All My Data")
    
    st.error("""
    **This will permanently delete:**
    - All uploaded documents and files
    - All financial data (income, expenses, debts, investments)
    - All chat history with AI
    - All vector embeddings
    - Document flags will be reset
    
    **Your account and profile information will remain intact.**
    """)
    
    # Confirmation checkboxes
    confirm1 = st.checkbox("I understand that this action cannot be undone")
    confirm2 = st.checkbox("I want to delete all my data and start fresh")
    
    if confirm1 and confirm2:
        delete_button = st.button("🗑️ DELETE ALL MY DATA", type="primary", use_container_width=True)
        
        if delete_button:
            with st.spinner("🗑️ Deleting all your data... Please wait..."):
                try:
                    session = SessionLocal()
                    
                    # 1. Delete vector embeddings
                    try:
                        from processors.vector_store_manager import VectorStoreManager
                        vector_store = VectorStoreManager()
                        collection_name = vector_store.get_user_collection_name(st.session_state.user_id)
                        try:
                            vector_store.chroma_client.delete_collection(collection_name)
                        except:
                            pass
                    except:
                        pass
                    
                    # 2. Delete files
                    for doc in documents:
                        if doc.file_path and os.path.exists(doc.file_path):
                            try:
                                os.remove(doc.file_path)
                            except:
                                pass
                    
                    # 3. Delete database records
                    session.query(ChatHistory).filter(ChatHistory.user_id == st.session_state.user_id).delete()
                    session.query(FinancialData).filter(FinancialData.user_id == st.session_state.user_id).delete()
                    session.query(Document).filter(Document.user_id == st.session_state.user_id).delete()
                    
                    # 4. Reset user flags
                    user_obj = session.query(User).filter(User.id == st.session_state.user_id).first()
                    
                    if user_obj:
                        user_obj.has_salary_slip = False
                        user_obj.has_bank_statement = False
                        user_obj.has_loan_data = False
                        user_obj.has_credit_card_statement = False
                        user_obj.has_collateral_details = False
                    
                    session.commit()
                    session.close()
                    
                    st.success("""
                    ✅ **All Data Deleted Successfully!**
                    
                    Your account has been cleaned. You can now upload fresh documents and data.
                    
                    The page will refresh in a moment...
                    """)
                    
                    st.balloons()
                    
                    # Wait a bit and refresh
                    import time
                    time.sleep(2)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error deleting data: {str(e)}")
                    if 'session' in locals():
                        session.rollback()
                        session.close()
    else:
        st.info("☑️ Check both boxes above to enable the delete button")

# Footer with completion status
st.divider()
st.subheader("✅ Document Checklist")

checklist = {
    "Salary Slip": user.has_salary_slip,
    "Bank Statement": user.has_bank_statement,
    "Loan Documents": user.has_loan_data,
    "Credit Card Statement": user.has_credit_card_statement,
    "Collateral Details": user.has_collateral_details
}

col1, col2 = st.columns(2)

for i, (item, status) in enumerate(checklist.items()):
    with col1 if i % 2 == 0 else col2:
        if status:
            st.success(f"✅ {item}")
        else:
            st.warning(f"⏳ {item}")

completion = sum(checklist.values()) / len(checklist) * 100
st.progress(completion / 100, text=f"Document Completion: {completion:.0f}%")