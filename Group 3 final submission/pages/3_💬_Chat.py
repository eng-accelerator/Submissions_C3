import streamlit as st
from utils.session_state import check_authentication
from database.db_manager import DBManager
from agents.ai_agents import AgentOrchestrator
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="AI Coach Chat", page_icon="💬", layout="wide")

# Check authentication
if not check_authentication():
    st.error("Please login first!")
    st.stop()

# Initialize
db = DBManager()
user = db.get_user_by_id(st.session_state.user_id)

# Get API key
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')

if not OPENROUTER_API_KEY:
    st.error("⚠️ OpenRouter API key not found in .env file. Please add OPENROUTER_API_KEY.")
    st.info("Get your API key from: https://openrouter.ai/")
    st.stop()

# Initialize Agent Orchestrator
@st.cache_resource
def get_agent_orchestrator():
    return AgentOrchestrator(openrouter_api_key=OPENROUTER_API_KEY)

try:
    agent_orchestrator = get_agent_orchestrator()
except Exception as e:
    st.error(f"Failed to initialize AI agents: {str(e)}")
    st.info("Please check your OPENROUTER_API_KEY in .env file")
    st.stop()

# Page Title
st.title("💬 AI Financial Coach - Chat")

# Sidebar - Agent Selection
with st.sidebar:
    st.subheader("🤖 Select AI Agent")
    
    agent_options = {
        "Auto-Select (Recommended)": None,
        "💳 Debt Analyzer": "debt_analyzer",
        "💰 Savings Strategist": "savings_strategy",
        "📈 Investment Advisor": "investment_advisor",
        "📊 Budget Planner": "budget_planner",
        "🏖️ Retirement Planner": "retirement_planner"
    }
    
    selected_agent = st.selectbox(
        "Choose Agent",
        options=list(agent_options.keys()),
        help="Auto-Select will intelligently route your question to the right agent"
    )
    
    st.divider()
    
    st.subheader("📋 Quick Questions")
    if st.button("💳 Analyze my debt", use_container_width=True):
        st.session_state.quick_query = "Can you analyze my debt and suggest a plan to repay it?"
    
    if st.button("🏖️ Retirement planning", use_container_width=True):
        st.session_state.quick_query = "Can you help me prepare an early retirement plan?"
    
    if st.button("🏠 Buy asset advice", use_container_width=True):
        st.session_state.quick_query = "I want to buy another asset. What should I consider?"
    
    if st.button("📈 Investment portfolio", use_container_width=True):
        st.session_state.quick_query = "Please help me build an investment portfolio."
    
    st.divider()
    
    # User stats
    st.subheader("📊 Your Profile")
    st.write(f"**Name:** {user.full_name or user.username}")
    st.write(f"**Income:** ₹{user.monthly_income:,.0f}/mo" if user.monthly_income else "**Income:** Not set")
    
    # Document status
    docs_uploaded = sum([
        user.has_salary_slip,
        user.has_bank_statement,
        user.has_loan_data,
        user.has_credit_card_statement,
        user.has_collateral_details
    ])
    st.write(f"**Documents:** {docs_uploaded}/5 uploaded")
    
    if docs_uploaded < 3:
        st.warning("📄 Upload more documents for better insights!")

# Initialize chat history in session state
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []
    # Add welcome message
    st.session_state.chat_messages.append({
        'role': 'assistant',
        'content': f"""Hello {user.full_name or user.username}! 👋

I'm your AI Financial Coach, powered by multiple specialized agents. I can help you with:

💳 **Debt Analysis** - Understand and optimize your debt repayment
💰 **Savings Strategy** - Build emergency funds and savings plans  
📈 **Investment Advice** - Create diversified investment portfolios
📊 **Budget Planning** - Optimize your monthly budget
🏖️ **Retirement Planning** - Plan for a comfortable retirement

What would you like to discuss today?""",
        'agent': 'system'
    })

# Check for quick query
if 'quick_query' in st.session_state:
    user_query = st.session_state.quick_query
    del st.session_state.quick_query
else:
    user_query = None

# Display chat messages
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if message.get('agent') and message['agent'] != 'system':
                st.caption(f"🤖 Agent: {message['agent'].replace('_', ' ').title()}")

# Chat input
if prompt := st.chat_input("Ask me anything about your finances...") or user_query:
    # Use quick query if available, otherwise use typed prompt
    user_message = user_query if user_query else prompt
    
    # Add user message to chat
    st.session_state.chat_messages.append({
        'role': 'user',
        'content': user_message
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_message)
    
    # Process with AI agent
    with st.chat_message("assistant"):
        with st.spinner("🤔 Analyzing your query..."):
            # Get user's financial data as context for AI
            context = ""
            
            try:
                # Get all financial data
                all_financial_data = db.get_financial_data(st.session_state.user_id)
                
                # Separate by type
                expenses = [d for d in all_financial_data if d.data_type == 'expense']
                incomes = [d for d in all_financial_data if d.data_type == 'income']
                debts = [d for d in all_financial_data if d.data_type == 'debt']
                investments = [d for d in all_financial_data if d.data_type == 'investment']
                
                # Build context string with actual data
                context_parts = []
                
                if expenses:
                    context_parts.append("EXPENSES:")
                    for e in expenses[-10:]:  # Last 10 expenses
                        context_parts.append(f"- {e.category}: ₹{e.amount:,.2f} on {e.transaction_date.strftime('%Y-%m-%d') if e.transaction_date else 'N/A'} - {e.description or ''}")
                
                if debts:
                    context_parts.append("\nDEBTS:")
                    for d in debts:
                        context_parts.append(f"- {d.category}: ₹{d.amount:,.2f} - {d.description or ''}")
                
                if incomes:
                    context_parts.append("\nINCOME:")
                    for i in incomes:
                        context_parts.append(f"- {i.category}: ₹{i.amount:,.2f} - {i.description or ''}")
                
                if investments:
                    context_parts.append("\nINVESTMENTS:")
                    for inv in investments:
                        context_parts.append(f"- {inv.category}: ₹{inv.amount:,.2f} - {inv.description or ''}")
                
                context = "\n".join(context_parts)
                
            except Exception as e:
                context = ""
                st.caption(f"Note: Could not load financial data context")
            
            # Determine which agent to use
            agent_to_use = agent_options[selected_agent]
            
            # Process query
            result = agent_orchestrator.process_query(
                user_id=st.session_state.user_id,
                query=user_message,
                context=context,
                specific_agent=agent_to_use
            )
            
            if result['success']:
                response = result['response']
                agent_used = result['agent']
                
                st.markdown(response)
                st.caption(f"🤖 Agent: {agent_used.replace('_', ' ').title()}")
                
                # Save to chat history in database
                db.add_chat_message(
                    user_id=st.session_state.user_id,
                    message=user_message,
                    response=response,
                    agent_type=agent_used
                )
                
                # Add to session state
                st.session_state.chat_messages.append({
                    'role': 'assistant',
                    'content': response,
                    'agent': agent_used
                })
            else:
                error_msg = f"I encountered an error: {result.get('error', 'Unknown error')}. Please try again."
                st.error(error_msg)
                st.session_state.chat_messages.append({
                    'role': 'assistant',
                    'content': error_msg,
                    'agent': 'error'
                })

# Clear chat button
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.chat_messages = []
        st.rerun()

# Display recent chats from database
with st.expander("📜 View Previous Chat Sessions"):
    chat_history = db.get_chat_history(st.session_state.user_id, limit=10)
    
    if chat_history:
        for chat in chat_history:
            st.markdown(f"""
**{chat.created_at.strftime('%Y-%m-%d %H:%M')}** - Agent: {chat.agent_type or 'General'}

**You:** {chat.message}

**AI Coach:** {chat.response[:200]}{'...' if len(chat.response) > 200 else ''}

---
""")
    else:
        st.info("No previous chat sessions found.")

# Help section
with st.expander("❓ How to use AI Financial Coach"):
    st.markdown("""
### Getting Started

1. **Upload Documents** - Go to Profile page and upload your financial documents (optional)
2. **Choose an Agent** - Select a specific agent or use Auto-Select
3. **Ask Questions** - Type your financial queries naturally
4. **Get Personalized Advice** - Receive AI-powered recommendations

### Example Questions

**Debt Management:**
- "How can I pay off my credit card debt faster?"
- "Should I consolidate my loans?"
- "Create a debt repayment plan for me"

**Savings:**
- "How much should I save for emergencies?"
- "What's the best way to save for a down payment?"
- "Help me build a 6-month emergency fund"

**Investments:**
- "Build me a diversified investment portfolio"
- "Should I invest in equity or debt funds?"
- "What SIP amount should I start with?"

**Budget:**
- "Create a monthly budget for me"
- "Where am I overspending?"
- "Apply the 50-30-20 rule to my finances"

**Retirement:**
- "How much do I need for retirement?"
- "Can I retire early at 50?"
- "Compare NPS vs PPF for retirement"

### Tips for Best Results

✅ Be specific in your questions
✅ Provide context about your goals
✅ Ask follow-up questions for clarity
✅ Upload documents for personalized advice (optional)
    """)