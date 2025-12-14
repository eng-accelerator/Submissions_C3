import streamlit as st
from utils.session_state import check_authentication
from database.db_manager import DBManager
from processors.rag_system import RAGSystem
from datetime import datetime
import os
import requests
import re

st.set_page_config(page_title="AI Chat", page_icon="💬", layout="wide")

# Check authentication
if not check_authentication():
    st.error("Please login first!")
    st.stop()

db = DBManager()
user = db.get_user_by_id(st.session_state.user_id)
rag = RAGSystem(db_manager=db)

st.title("💬 AI Financial Coach")

# Get stats
documents = db.get_user_documents(user.id)
total_docs = len(documents)

try:
    vector_stats = rag.vector_store.get_collection_stats(user.id)
    total_chunks = vector_stats.get('total_chunks', 0)
except:
    total_chunks = 0

# Display stats
col1, col2 = st.columns(2)
with col1:
    st.metric("📄 Documents", total_docs)
with col2:
    st.metric("📊 Indexed Chunks", total_chunks)

st.divider()

if total_chunks == 0:
    st.warning("⚠️ No documents indexed. Run: `python test_direct_add.py`")
    st.stop()

# Quick Questions
st.caption("💡 Quick Questions:")
quick_qs = {
    "What is my credit limit?": "credit limit",
    "What is the due date?": "due date payment date",
    "What is the total amount due?": "total amount due",
    "What is the minimum payment?": "minimum payment",
    "Show recent transactions": "transactions charges"
}

cols = st.columns(len(quick_qs))
for i, (question, _) in enumerate(quick_qs.items()):
    if cols[i].button(question, key=f"q_{i}", use_container_width=True):
        st.session_state.current_query = question

# Main query input
query = st.text_input(
    "Ask a question:",
    value=st.session_state.get('current_query', ''),
    placeholder="e.g., What is my credit card balance?",
    key="query_input"
)

if st.button("🔍 Ask", type="primary", use_container_width=True) and query:
    with st.spinner("Analyzing your documents..."):
        # Search documents
        results = rag.query_documents(user_id=user.id, query=query, k=5)
        
        if results:
            # Combine all context
            context_parts = []
            for r in results:
                source = r['metadata'].get('file_name', 'document')
                content = r['content']
                context_parts.append(f"[From {source}]\n{content}")
            
            full_context = "\n\n".join(context_parts)
            
            # Enhanced prompt for better extraction
            prompt = f"""You are analyzing financial documents to answer the user's question. Be extremely precise and extract exact values.

IMPORTANT RULES:
1. If asking for a specific number (amount, date, limit), extract ONLY that exact number from the documents
2. Quote the exact amount/date as written in the documents
3. If multiple values are found, list them clearly
4. If the answer is not in the documents, say "I cannot find this information in your documents"
5. Do NOT make up or estimate numbers
6. Keep answers SHORT - typically 1-2 sentences

User's Question: {query}

Documents Content:
{full_context}

Answer (be precise and concise):"""

            try:
                api_key = os.getenv('OPENROUTER_API_KEY')
                
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "anthropic/claude-3.5-sonnet",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 300,
                        "temperature": 0.1  # Low temperature for factual extraction
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    
                    # Display answer
                    st.markdown("### 🤖 Answer")
                    st.info(answer)
                    
                    # Show sources
                    with st.expander("📄 View Source Documents", expanded=False):
                        for i, result in enumerate(results, 1):
                            file_name = result['metadata'].get('file_name', 'Unknown')
                            st.markdown(f"**Source {i}: {file_name}**")
                            st.text(result['content'][:400])
                            st.divider()
                    
                    # Option to see raw results
                    with st.expander("🔍 View Raw Search Results", expanded=False):
                        for i, result in enumerate(results, 1):
                            st.markdown(f"**Result {i}** (Score: {result.get('similarity_score', 0):.3f})")
                            st.write(result['content'])
                            st.caption(f"From: {result['metadata'].get('file_name', 'N/A')}")
                            st.divider()
                else:
                    st.error(f"API Error: {response.status_code}")
                    st.json(response.json())
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
                # Fallback: show raw results
                st.warning("Showing raw search results instead:")
                for i, result in enumerate(results, 1):
                    with st.expander(f"Result {i}: {result['metadata'].get('file_name', 'Unknown')}"):
                        st.write(result['content'])
        else:
            st.warning("❌ No relevant information found. Try rephrasing your question.")

st.divider()

# Document info
with st.expander("📚 My Documents"):
    if documents:
        for doc in documents:
            st.write(f"• {doc.file_name}")

# Help section
with st.expander("💡 Tips for Better Results"):
    st.markdown("""
    **Best Questions:**
    - ✅ "What is my credit limit?"
    - ✅ "When is the payment due?"
    - ✅ "What is the total amount due?"
    - ✅ "What transactions are listed?"
    
    **Avoid:**
    - ❌ Vague questions like "Tell me about my finances"
    - ❌ Questions about data not in your documents
    
    **If answers seem wrong:**
    - Check the source documents (expand "View Source Documents")
    - Try being more specific in your question
    - Verify the correct documents are uploaded
    """)

# Debug section
if st.checkbox("🔧 Show Debug Info"):
    st.write(f"**User ID:** {user.id}")
    st.write(f"**Total Chunks:** {total_chunks}")
    st.write(f"**Documents:** {total_docs}")
    
    if st.button("Test Search"):
        test = rag.query_documents(user.id, "credit limit", k=3)
        st.write(f"Test search returned {len(test)} results")
        if test:
            st.write("Sample result:")
            st.code(test[0]['content'][:300])