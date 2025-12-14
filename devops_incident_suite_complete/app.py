import streamlit as st
from orchestration.graph import IncidentAnalysisGraph
from utils.rag_engine import RAGEngine
from utils.chat_handler import ChatHandler
from utils.export import export_to_json, export_to_markdown, export_to_csv
from utils.integrations import SlackIntegration, JiraIntegration
from config.settings import settings
from datetime import datetime
import os

# Page config
st.set_page_config(
    page_title="DevOps Incident Suite",
    page_icon="🚨",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .incident-card {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid;
        margin: 0.5rem 0;
    }
    .p0 {border-left-color: #ff4444;}
    .p1 {border-left-color: #ff8800;}
    .p2 {border-left-color: #ffbb00;}
    .p3 {border-left-color: #4444ff;}
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'graph' not in st.session_state:
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    if not api_key:
        st.error("⚠️ Please set OPENROUTER_API_KEY environment variable")
        st.info("""
        **How to get OpenRouter API Key:**
        1. Visit https://openrouter.ai/
        2. Sign up / Login
        3. Go to Keys section
        4. Create a new API key
        5. Ensure you have credits for OpenAI models
        6. Set as environment variable: `export OPENROUTER_API_KEY="your-key"`
        """)
        st.stop()
    
    # Initialize RAG engine with LanceDB and API keys for embeddings
    rag_engine = RAGEngine(
        settings.lancedb_path, 
        openrouter_api_key=api_key,
        huggingface_api_key=settings.huggingface_api_key
    )
    st.session_state.graph = IncidentAnalysisGraph(api_key, settings.model_name, rag_engine)
    st.session_state.results = None
    st.session_state.chat_history = []
    st.session_state.chat_handler = ChatHandler(
        st.session_state.graph.client,
        settings.model_name
    )

# Header
st.title("🚨 Multi-Agent DevOps Incident Analysis Suite")
st.markdown(f"**Powered by LangGraph + OpenRouter ({settings.model_name}) + LanceDB**")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Model selection - OpenAI and Claude models
    st.subheader("🤖 Model Selection")
    model_options = {
        "Claude Sonnet 4 (Recommended)": "anthropic/claude-sonnet-4-20250514",
        "Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
        "GPT-4 Turbo": "openai/gpt-4-turbo",
        "GPT-4": "openai/gpt-4",
        "GPT-3.5 Turbo (Fast)": "openai/gpt-3.5-turbo"
    }
    
    selected_model = st.selectbox(
        "Choose Model",
        options=list(model_options.keys()),
        index=0
    )
    settings.model_name = model_options[selected_model]
    st.session_state.graph.model = settings.model_name
    st.session_state.chat_handler.model = settings.model_name
    
    # Update all agent models
    st.session_state.graph.log_classifier.model = settings.model_name
    st.session_state.graph.remediation_agent.model = settings.model_name
    st.session_state.graph.notification_agent.model = settings.model_name
    st.session_state.graph.cookbook_agent.model = settings.model_name
    st.session_state.graph.jira_agent.model = settings.model_name
    
    st.success(f"✓ Using: `{settings.model_name}`")
    
    st.divider()
    st.subheader("📊 System Stats")
    if st.session_state.graph:
        stats = st.session_state.graph.rag_engine.get_incident_statistics()
        st.metric("Historical Incidents", stats.get("total_incidents", 0))
        st.metric("Avg Resolution", stats.get("avg_resolution_time", "N/A"))
        
        # API usage
        usage = st.session_state.graph.client.get_usage_stats()
        st.metric("Tokens Used", f"{usage['total_tokens']:,}")
    
    st.divider()
    st.subheader("🔧 Features")
    st.checkbox("Enable RAG (LanceDB)", value=True, key="enable_rag")
    st.checkbox("Auto-create JIRA tickets", value=True, key="auto_jira")
    st.checkbox("Send Slack notifications", value=False, key="auto_slack")
    
    st.divider()
    st.subheader("📝 Sample Data")
    if st.button("Load Sample Logs", use_container_width=True):
        try:
            with open("data/sample_logs.txt", "r") as f:
                st.session_state.sample_logs = f.read()
            st.success("✓ Sample logs loaded!")
        except FileNotFoundError:
            st.error("sample_logs.txt not found in data/ folder")

# Main content - Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📝 Analysis", "💬 Chat Assistant", "📊 Dashboard", "🔍 RAG Explorer"])

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Input Logs")
        logs = st.text_area(
            "Paste your ops logs here",
            value=st.session_state.get("sample_logs", ""),
            height=200,
            key="log_input",
            placeholder="Paste logs or click 'Load Sample Logs' in sidebar..."
        )
        
        if st.button("🚀 Analyze Incidents", type="primary", use_container_width=True):
            if logs:
                with st.spinner(f"Running multi-agent analysis with {settings.model_name}..."):
                    try:
                        results = st.session_state.graph.run(logs)
                        st.session_state.results = results
                        st.success("✅ Analysis complete!")
                        st.balloons()
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("Check your API key and ensure you have credits for OpenAI models")
            else:
                st.warning("Please enter logs or load sample logs first")
    
    with col2:
        if st.session_state.results:
            st.subheader("Quick Stats")
            summary = st.session_state.results.get("incident_summary", {})
            
            st.metric("Total Incidents", summary.get("totalIncidents", 0))
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🔴 P0", summary.get("critical", 0))
                st.metric("🟡 P2", summary.get("medium", 0))
            with col_b:
                st.metric("🟠 P1", summary.get("high", 0))
                st.metric("🔵 P3", summary.get("low", 0))
    
    # Results Display
    if st.session_state.results:
        st.divider()
        
        # Incidents
        st.subheader("📋 Classified Incidents")
        incidents = st.session_state.results.get("classified_incidents", [])
        for inc in incidents:
            severity_class = inc['severity'].lower()
            st.markdown(f"""
            <div class="incident-card {severity_class}">
                <strong>{inc['severity']}</strong> - {inc['id']}<br>
                <small>{inc['service']}</small><br>
                {inc['description']}
            </div>
            """, unsafe_allow_html=True)
        
        # Remediations
        st.subheader("⚡ Remediation Plans")
        remediations = st.session_state.results.get("remediations", [])
        for rem in remediations:
            with st.expander(f"🔧 Remediation for {rem['incidentId']}"):
                st.write(f"**Priority:** {rem.get('priority', 'N/A')}")
                st.write(f"**Estimated Time:** {rem.get('estimatedTotalTime', 'N/A')}")
                st.write(f"**Risk Level:** {rem.get('riskLevel', 'N/A')}")
                st.divider()
                for fix in rem['fixes']:
                    st.markdown(f"**Step {fix['step']}:** {fix['action']}")
                    st.caption(f"💡 {fix['rationale']}")
                    if fix.get('command'):
                        st.code(fix['command'], language="bash")
                    st.caption(f"⏱️ {fix['estimatedTime']} | ✅ Verify: {fix['verification']}")
                    st.divider()
        
        # Notifications
        st.subheader("📢 Slack Notifications")
        notifications = st.session_state.results.get("notifications", [])
        
        if notifications:
            # Send to Slack if enabled
            if st.session_state.get("auto_slack", False) and settings.slack_webhook_url:
                try:
                    slack_integration = SlackIntegration(settings.slack_webhook_url)
                    sent_count = 0
                    for notif in notifications:
                        if slack_integration.send_notification(notif):
                            sent_count += 1
                    
                    if sent_count > 0:
                        st.success(f"✅ Sent {sent_count} notification(s) to Slack!")
                    else:
                        st.warning("⚠️ Failed to send notifications to Slack. Check your webhook URL.")
                except Exception as e:
                    st.error(f"❌ Error sending to Slack: {str(e)}")
            elif st.session_state.get("auto_slack", False) and not settings.slack_webhook_url:
                st.warning("⚠️ Slack webhook URL not configured. Add SLACK_WEBHOOK_URL to your .env file.")
            else:
                # Show button to manually send
                if settings.slack_webhook_url:
                    if st.button("📤 Send to Slack", type="primary"):
                        try:
                            slack_integration = SlackIntegration(settings.slack_webhook_url)
                            sent_count = 0
                            for notif in notifications:
                                if slack_integration.send_notification(notif):
                                    sent_count += 1
                            
                            if sent_count > 0:
                                st.success(f"✅ Sent {sent_count} notification(s) to Slack!")
                                st.balloons()
                            else:
                                st.error("❌ Failed to send notifications. Check your webhook URL.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.info("💡 Enable 'Send Slack notifications' in sidebar and configure SLACK_WEBHOOK_URL in .env to send automatically")
        
        for notif in notifications:
            msg = notif['message']
            st.info(f"{notif['urgency']} **{msg['title']}** → {notif['channel']}")
            with st.expander("View Details"):
                st.write(f"**Summary:** {msg['summary']}")
                st.write(f"**Impact:** {msg.get('impact', 'N/A')}")
                st.write("**Actions:**")
                for action in msg['actions']:
                    st.write(f"- {action}")
                st.write(f"**Assignees:** {', '.join(msg['assignees'])}")
        
        # JIRA Tickets
        st.subheader("🎫 JIRA Tickets (P0/P1)")
        tickets = st.session_state.results.get("jira_tickets", [])
        for ticket in tickets:
            with st.expander(f"{ticket['priority']} - {ticket['title']}"):
                st.write(f"**Type:** {ticket['type']}")
                st.write(f"**Description:** {ticket['description']}")
                st.write(f"**Labels:** {', '.join(ticket['labels'])}")
                st.write(f"**Estimated Effort:** {ticket['estimatedEffort']}")
                if ticket.get('remediationSteps'):
                    st.write("**Remediation Steps:**")
                    for step in ticket['remediationSteps']:
                        st.write(f"- {step}")
        
        # Cookbooks
        st.subheader("📖 Operational Cookbooks")
        cookbooks = st.session_state.results.get("cookbooks", [])
        for cb in cookbooks:
            with st.expander(f"📗 {cb['title']}"):
                st.write(f"**Incident Type:** {cb['incidentType']}")
                st.write(f"**Applicable Services:** {', '.join(cb['applicableServices'])}")
                for phase in cb['checklist']:
                    st.write(f"### {phase['phase']}")
                    for step in phase['steps']:
                        st.write(f"{step['step']}. {step['task']}")
                        st.caption(f"✓ {step['checkpoint']}")
        
        # Export Section
        st.divider()
        st.subheader("📥 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            json_data = export_to_json(st.session_state.results)
            st.download_button(
                label="📄 Export JSON",
                data=json_data,
                file_name=f"incident_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            md_data = export_to_markdown(st.session_state.results)
            st.download_button(
                label="📝 Export Markdown",
                data=md_data,
                file_name=f"incident_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        
        with col3:
            csv_data = export_to_csv(st.session_state.results)
            st.download_button(
                label="📊 Export CSV",
                data=csv_data,
                file_name=f"incidents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

with tab2:
    st.subheader("💬 Chat with Incident Assistant")
    st.info("Ask questions about the analyzed incidents or request specific information")
    
    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
    
    # Chat input using form (works inside tabs and supports Enter key)
    # Note: st.chat_input() doesn't work inside tabs, so we use st.form() instead
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            prompt = st.text_input(
                "Type your message:",
                key="chat_input",
                placeholder="Ask about incidents...",
                label_visibility="collapsed"
            )
        with col2:
            st.write("")  # Spacing
            submit_button = st.form_submit_button("Send", type="primary", use_container_width=True)
        
        # Handle form submission inside form context to capture prompt value
        if submit_button and prompt:
            # Store prompt in session state before form clears
            st.session_state.pending_prompt = prompt
    
    # Handle the pending prompt (process outside form to avoid display issues)
    if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
        prompt_to_process = st.session_state.pending_prompt
        del st.session_state.pending_prompt  # Clear it
        
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_process})
        
        # Get assistant response
        if st.session_state.results:
            # Show spinner while processing
            with st.spinner("Thinking..."):
                response = st.session_state.chat_handler.handle_query(
                    prompt_to_process,
                    st.session_state.results,
                    st.session_state.chat_history
                )
                
                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response
                })
        else:
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ Please run an analysis first to enable the chat assistant."
            })
        
        # Rerun to show new messages
        st.rerun()

with tab3:
    st.subheader("📊 Analytics Dashboard")
    
    if st.session_state.results:
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Resolution Time", "15 min")
        with col2:
            services = st.session_state.results.get("incident_summary", {}).get("affectedServices", [])
            st.metric("Affected Services", len(services))
        with col3:
            st.metric("Automation Coverage", "78%")
        with col4:
            usage = st.session_state.graph.client.get_usage_stats()
            st.metric("Total Tokens", f"{usage['total_tokens']:,}")
        
        st.divider()
        
        # Service breakdown
        st.subheader("Service Impact Analysis")
        services_data = {}
        for inc in st.session_state.results.get("classified_incidents", []):
            service = inc['service']
            severity = inc['severity']
            if service not in services_data:
                services_data[service] = {'P0': 0, 'P1': 0, 'P2': 0, 'P3': 0}
            services_data[service][severity] += 1
        
        for service, counts in services_data.items():
            st.write(f"**{service}:**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("P0", counts['P0'])
            col2.metric("P1", counts['P1'])
            col3.metric("P2", counts['P2'])
            col4.metric("P3", counts['P3'])
    else:
        st.info("Run an analysis to see dashboard metrics")

with tab4:
    st.subheader("🔍 RAG Explorer (LanceDB)")
    st.write("Search historical incidents using semantic similarity")
    
    query = st.text_input("Search query:", placeholder="e.g., database timeout")
    n_results = st.slider("Number of results", 1, 10, 3)
    
    if st.button("Search", type="primary"):
        if query:
            with st.spinner("Searching LanceDB..."):
                similar = st.session_state.graph.rag_engine.retrieve_similar_incidents(query, n_results=n_results)
                
                if similar:
                    st.success(f"Found {len(similar)} similar incidents")
                    for idx, inc in enumerate(similar, 1):
                        with st.expander(f"Result {idx}: {inc.get('description', 'N/A')[:100]}..."):
                            st.json(inc)
                else:
                    st.info("No similar incidents found in database")
        else:
            st.warning("Please enter a search query")

# Footer
st.divider()
st.caption(f"Built with LangGraph + OpenRouter ({settings.model_name}) + LanceDB")