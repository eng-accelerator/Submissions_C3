"""
Cybersecurity Multi-Agent System - Streamlit Web Interface
Hosted on Hugging Face Spaces
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Import the coordinator
try:
    from coordinator_langgraph import LangGraphCoordinator
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    st.error(f"⚠️ LangGraph not available. Please install: pip install langgraph")
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error importing coordinator: {e}")
    import traceback
    st.code(traceback.format_exc())
    st.stop()

# Page configuration (must be first Streamlit command)
st.set_page_config(
    page_title="Cybersecurity Multi-Agent System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Early exit if coordinator not available (before any other Streamlit commands)
if not LANGGRAPH_AVAILABLE:
    st.error("⚠️ LangGraph not available. Please install: pip install langgraph")
    st.stop()

# Custom CSS for soft professional styling
st.markdown("""
    <style>
    /* Main Header - Soft and Subtle */
    .main-header {
        font-size: 3rem;
        font-weight: 600;
        color: #E8EAED;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: 1px;
    }
    
    /* Subtitle */
    h3 {
        color: #9AA0A6 !important;
        text-align: center;
        font-weight: 300;
        letter-spacing: 0.5px;
    }
    
    /* Agent Cards - Soft Background */
    .agent-card {
        background-color: #252836;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #6B8E9F;
        border: 1px solid rgba(107, 142, 159, 0.2);
    }
    
    .agent-card:hover {
        border-color: rgba(107, 142, 159, 0.4);
    }
    
    /* Alert Styling - Soft Colors */
    .alert-critical {
        background-color: rgba(220, 53, 69, 0.08);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #C84E5C;
        margin: 0.5rem 0;
    }
    
    .alert-high {
        background-color: rgba(255, 152, 0, 0.08);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #D4A574;
        margin: 0.5rem 0;
    }
    
    .alert-medium {
        background-color: rgba(255, 193, 7, 0.08);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #D4B86A;
        margin: 0.5rem 0;
    }
    
    .alert-low {
        background-color: rgba(76, 175, 80, 0.08);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 3px solid #81A684;
        margin: 0.5rem 0;
    }
    
    /* Metric Cards - Subtle */
    .metric-card {
        background-color: #252836;
        color: #E8EAED;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
        border: 1px solid rgba(107, 142, 159, 0.15);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #1A1D29;
    }
    
    /* Button Styling - Soft */
    .stButton > button {
        background-color: #6B8E9F;
        color: #FFFFFF;
        font-weight: 500;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1.5rem;
        transition: background-color 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #7A9FB0;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #252836;
        color: #9AA0A6;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 0.75rem 1.5rem;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #6B8E9F;
        color: #FFFFFF;
        font-weight: 500;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: #252836;
        color: #E8EAED;
        border: 1px solid rgba(107, 142, 159, 0.2);
    }
    
    .stTextArea > div > div > textarea {
        background-color: #252836;
        color: #E8EAED;
        border: 1px solid rgba(107, 142, 159, 0.2);
    }
    
    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #252836;
        color: #E8EAED;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #252836;
        color: #E8EAED;
        border-radius: 0.5rem;
    }
    
    /* Divider */
    hr {
        border-color: rgba(107, 142, 159, 0.15);
        margin: 1.5rem 0;
    }
    
    /* Info/Warning/Success Boxes - Soft */
    .stInfo {
        background-color: rgba(107, 142, 159, 0.08);
        border-left: 3px solid #6B8E9F;
    }
    
    .stSuccess {
        background-color: rgba(76, 175, 80, 0.08);
        border-left: 3px solid #81A684;
    }
    
    .stWarning {
        background-color: rgba(255, 193, 7, 0.08);
        border-left: 3px solid #D4B86A;
    }
    
    .stError {
        background-color: rgba(220, 53, 69, 0.08);
        border-left: 3px solid #C84E5C;
    }
    
    /* Code Blocks */
    .stCode {
        background-color: #252836;
        border: 1px solid rgba(107, 142, 159, 0.2);
        border-radius: 0.5rem;
    }
    
    /* JSON Display */
    .stJson {
        background-color: #252836;
        border: 1px solid rgba(107, 142, 159, 0.2);
        border-radius: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar - Soft */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1A1D29;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #6B8E9F;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #7A9FB0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'coordinator' not in st.session_state:
    st.session_state.coordinator = None
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Initialize coordinator
@st.cache_resource
def get_coordinator():
    """Initialize and cache the coordinator"""
    try:
        config = {}
        coordinator = LangGraphCoordinator(config)
        coordinator.start_monitoring()
        return coordinator
    except Exception as e:
        st.error(f"Error initializing coordinator: {e}")
        return None

# Header with soft professional theme
st.markdown("""
    <div style="text-align: center; padding: 2rem 0; margin-bottom: 2rem;">
        <h1 class="main-header">🛡️ Cybersecurity Multi-Agent System</h1>
        <h3 style="color: #9AA0A6; font-weight: 300; letter-spacing: 0.5px; margin-top: 0.5rem;">
            Real-time threat detection, vulnerability scanning, and incident response
        </h3>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Initialize coordinator
    if st.button("🔄 Initialize System", use_container_width=True):
        with st.spinner("Initializing agents..."):
            st.session_state.coordinator = get_coordinator()
            if st.session_state.coordinator:
                st.success("✅ System initialized!")
            else:
                st.error("❌ Failed to initialize")
    
    st.divider()
    
    # Demo mode
    use_demo = st.checkbox("📋 Use Demo Data", value=True, help="Use sample data for demonstration")
    
    if use_demo:
        st.info("💡 Demo mode uses sample data. Uncheck to use your own data.")
    
    st.divider()
    
    # Agent status
    if st.session_state.coordinator:
        st.header("🤖 Agent Status")
        status = st.session_state.coordinator.get_system_status()
        for agent_id, agent_status in status.get("agents", {}).items():
            agent_name = agent_status.get("agent_name", agent_id)
            agent_stat = agent_status.get("status", "unknown")
            emoji = "🟢" if agent_stat == "monitoring" else "🟡"
            st.write(f"{emoji} {agent_name}: {agent_stat}")

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔍 Analysis", "📈 Results", "ℹ️ About"])

with tab1:
    st.header("📊 System Dashboard")
    
    if not st.session_state.coordinator:
        st.warning("⚠️ Please initialize the system from the sidebar first.")
    else:
        # Get system status
        status = st.session_state.coordinator.get_system_status()
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alerts", status.get("total_alerts", 0))
        
        with col2:
            alerts_by_sev = status.get("alerts_by_severity", {})
            critical = alerts_by_sev.get("critical", 0)
            st.metric("Critical Alerts", critical, delta=None, delta_color="inverse")
        
        with col3:
            workflows = status.get("workflows_executed", 0)
            st.metric("Workflows Executed", workflows)
        
        with col4:
            framework = status.get("framework", "Unknown")
            st.metric("Framework", framework)
        
        st.divider()
        
        # Alerts by severity chart
        if alerts_by_sev:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Alerts by Severity")
                fig_pie = px.pie(
                    values=list(alerts_by_sev.values()),
                    names=list(alerts_by_sev.keys()),
                    color_discrete_map={
                        "critical": "#d32f2f",
                        "high": "#f57c00",
                        "medium": "#fbc02d",
                        "low": "#388e3c"
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.subheader("Alerts by Agent")
                alerts_by_agent = status.get("alerts_by_agent", {})
                if alerts_by_agent:
                    fig_bar = px.bar(
                        x=list(alerts_by_agent.keys()),
                        y=list(alerts_by_agent.values()),
                        labels={"x": "Agent", "y": "Alerts"},
                        color=list(alerts_by_agent.values()),
                        color_continuous_scale="Blues"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        # Agent capabilities
        st.subheader("🤖 Agent Capabilities")
        if st.session_state.coordinator:
            agents = st.session_state.coordinator.agents
            for agent_id, agent in agents.items():
                with st.expander(f"📌 {agent.agent_name}"):
                    capabilities = agent.get_capabilities()
                    st.json(capabilities)

with tab2:
    st.header("🔍 Security Analysis")
    
    if not st.session_state.coordinator:
        st.warning("⚠️ Please initialize the system from the sidebar first.")
    else:
        # Input section
        st.subheader("📥 Input Data")
        
        # Log entries
        st.markdown("#### 📝 Log Entries")
        log_input_method = st.radio(
            "Input method:",
            ["Text Input", "File Upload", "Demo Data"],
            horizontal=True
        )
        
        log_entries = []
        if log_input_method == "Text Input":
            log_text = st.text_area(
                "Enter log entries (one per line):",
                height=150,
                placeholder="Failed password for user admin from 192.168.1.100\nSELECT * FROM users WHERE id=1 OR 1=1--"
            )
            if log_text:
                log_entries = [line.strip() for line in log_text.split("\n") if line.strip()]
        elif log_input_method == "File Upload":
            uploaded_file = st.file_uploader("Upload log file", type=["txt", "log"])
            if uploaded_file:
                log_entries = [line.decode("utf-8").strip() for line in uploaded_file.readlines()]
        else:  # Demo data
            log_entries = [
                "2024-01-15 10:23:45 Failed password for user admin from 192.168.1.100",
                "2024-01-15 10:23:46 Failed password for user admin from 192.168.1.100",
                "2024-01-15 10:23:47 Failed password for user admin from 192.168.1.100",
                "2024-01-15 10:24:00 SELECT * FROM users WHERE id=1 OR 1=1--",
            ]
            st.code("\n".join(log_entries))
            st.success(f"✅ Using {len(log_entries)} demo log entries")
        
        st.info(f"📊 {len(log_entries)} log entries ready")
        
        # System info
        st.markdown("#### 🖥️ System Information")
        system_info_method = st.radio(
            "Input method:",
            ["JSON Input", "Form Input", "Demo Data"],
            horizontal=True,
            key="system_info_method"
        )
        
        system_info = {}
        if system_info_method == "JSON Input":
            system_json = st.text_area(
                "Enter system info as JSON:",
                height=100,
                placeholder='{"software": {"web_server": "Apache 2.0.0"}, "configuration": {"debug_mode": true}}'
            )
            if system_json:
                try:
                    system_info = json.loads(system_json)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
        elif system_info_method == "Form Input":
            col1, col2 = st.columns(2)
            with col1:
                web_server = st.text_input("Web Server", "Apache 2.0.0")
                debug_mode = st.checkbox("Debug Mode Enabled", True)
            with col2:
                password_length = st.number_input("Password Min Length", min_value=1, max_value=50, value=8)
                mfa_enabled = st.checkbox("MFA Enabled", False)
            
            system_info = {
                "software": {"web_server": web_server},
                "configuration": {"debug_mode": debug_mode},
                "password_policy": {"password_length": password_length},
                "access_control_policy": {"mfa_enabled": mfa_enabled}
            }
        else:  # Demo data
            system_info = {
                "software": {
                    "Apache": "1.9.0",  # Vulnerable version (<2.0.0)
                    "MySQL": "1.4.0",   # Vulnerable version (<1.5.0)
                    "Python": "3.8.0",
                    "Django": "3.2.0"
                },
                "configuration": {
                    "debug_mode": True,  # Will trigger insecure configuration alert
                    "ssl_enabled": False
                },
                "files": [
                    {
                        "path": "/config/api_keys.txt",
                        "content": "API_KEY=example_api_key_1234567890abcdefghijklmnopqrstuvwxyz"
                    },
                    {
                        "path": "/config/database.conf",
                        "content": "password=SuperSecret123!"
                    }
                ]
            }
            st.json(system_info)
            st.success(f"✅ Using demo system info with {len(system_info.get('software', {}))} software packages")
        
        # Threat indicators
        st.markdown("#### 🎯 Threat Indicators")
        indicators_method = st.radio(
            "Input method:",
            ["JSON Input", "Form Input", "Demo Data"],
            horizontal=True,
            key="indicators_method"
        )
        
        indicators = []
        if indicators_method == "JSON Input":
            indicators_json = st.text_area(
                "Enter threat indicators as JSON array:",
                height=80,
                placeholder='[{"ip_address": "192.168.100.50", "context": {"source": "firewall"}}]'
            )
            if indicators_json:
                try:
                    indicators = json.loads(indicators_json)
                except json.JSONDecodeError:
                    st.error("Invalid JSON format")
        elif indicators_method == "Form Input":
            ip_address = st.text_input("IP Address", "192.168.100.50")
            domain = st.text_input("Domain", "")
            if ip_address or domain:
                indicator = {}
                if ip_address:
                    indicator["ip_address"] = ip_address
                if domain:
                    indicator["domain"] = domain
                indicator["context"] = {"source": "manual_input"}
                indicators = [indicator]
        else:  # Demo data
            indicators = [
                {"ip_address": "192.168.100.50", "context": {"source": "firewall"}},
                {"ip_address": "192.168.100.100", "context": {"source": "ids", "threat_score": 85}},
                {"domain": "malicious-domain.com", "context": {"source": "threat_intel"}},
                {"ip_address": "203.0.113.50", "context": {"source": "firewall", "blocked": True}}
            ]
            st.json(indicators)
            st.success(f"✅ Using {len(indicators)} demo threat indicators")
        
        st.info(f"🎯 {len(indicators)} threat indicators ready")
        
        # Run analysis button
        st.divider()
        if st.button("🚀 Run Security Analysis", type="primary", use_container_width=True):
            if not log_entries and not system_info and not indicators:
                st.warning("⚠️ Please provide at least one input (logs, system info, or indicators)")
            else:
                with st.spinner("🔄 Processing through multi-agent system..."):
                    try:
                        # Prepare inputs
                        log_input = log_entries if log_entries else None
                        system_input = system_info if (system_info and len(system_info) > 0) else None
                        indicators_input = indicators if indicators else None
                        
                        # Show input summary
                        with st.expander("📋 Input Summary", expanded=False):
                            st.write(f"**Log Entries:** {len(log_entries) if log_entries else 0}")
                            st.write(f"**System Info:** {'✅ Present' if system_input else '❌ Missing'}")
                            st.write(f"**Threat Indicators:** {len(indicators) if indicators else 0}")
                        
                        result = st.session_state.coordinator.process_security_event(
                            log_entries=log_input,
                            system_info=system_input,
                            indicators=indicators_input
                        )
                        
                        # Show result summary
                        with st.expander("📊 Result Summary", expanded=False):
                            st.write(f"**Log Alerts:** {len(result.get('log_alerts', []))}")
                            st.write(f"**Threat Alerts:** {len(result.get('threat_alerts', []))}")
                            st.write(f"**Vulnerability Alerts:** {len(result.get('vulnerability_alerts', []))}")
                            st.write(f"**Policy Alerts:** {len(result.get('policy_alerts', []))}")
                            
                            if len(result.get('threat_alerts', [])) == 0 and indicators_input:
                                st.warning("⚠️ No threat alerts generated. Check threat intelligence agent.")
                            if len(result.get('vulnerability_alerts', [])) == 0 and system_input:
                                st.warning("⚠️ No vulnerability alerts generated. Check vulnerability scanner agent.")
                        
                        st.session_state.results = result
                        st.success("✅ Analysis complete!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {e}")
                        import traceback
                        st.code(traceback.format_exc())

with tab3:
    st.header("📈 Analysis Results")
    
    if not st.session_state.results:
        st.info("ℹ️ No results yet. Run an analysis in the 'Analysis' tab.")
    else:
        result = st.session_state.results
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        log_alerts = result.get("log_alerts", [])
        threat_alerts = result.get("threat_alerts", [])
        vuln_alerts = result.get("vulnerability_alerts", [])
        policy_alerts = result.get("policy_alerts", [])
        incidents = result.get("incidents", [])
        
        with col1:
            st.metric("Log Alerts", len(log_alerts))
        with col2:
            st.metric("Threat Alerts", len(threat_alerts))
        with col3:
            st.metric("Vulnerability Alerts", len(vuln_alerts))
        with col4:
            st.metric("Incidents", len(incidents))
        
        st.divider()
        
        # Alerts by severity
        all_alerts = log_alerts + threat_alerts + vuln_alerts + policy_alerts
        if all_alerts:
            severity_counts = Counter([alert.get("severity", "unknown") for alert in all_alerts])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Alerts by Severity")
                fig = px.bar(
                    x=list(severity_counts.keys()),
                    y=list(severity_counts.values()),
                    labels={"x": "Severity", "y": "Count"},
                    color=list(severity_counts.keys()),
                    color_discrete_map={
                        "critical": "#d32f2f",
                        "high": "#f57c00",
                        "medium": "#fbc02d",
                        "low": "#388e3c"
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("Alerts by Type")
                type_counts = Counter([alert.get("alert_type", "unknown") for alert in all_alerts])
                fig = px.pie(
                    values=list(type_counts.values()),
                    names=list(type_counts.keys())
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Detailed alerts
        st.subheader("📋 Detailed Alerts")
        
        alert_tabs = st.tabs(["Log Alerts", "Threat Alerts", "Vulnerability Alerts", "Policy Alerts"])
        
        with alert_tabs[0]:
            if log_alerts:
                for alert in log_alerts[:20]:  # Show first 20
                    severity = alert.get("severity", "medium")
                    css_class = f"alert-{severity}"
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    st.write(f"**Type:** {alert.get('alert_type', 'unknown')}")
                    st.write(f"**Severity:** {severity.upper()}")
                    st.write(f"**Description:** {alert.get('description', '')}")
                    st.write(f"**Time:** {alert.get('timestamp', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No log alerts")
        
        with alert_tabs[1]:
            if threat_alerts:
                for alert in threat_alerts:
                    severity = alert.get("severity", "medium")
                    css_class = f"alert-{severity}"
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    st.write(f"**Type:** {alert.get('alert_type', 'unknown')}")
                    st.write(f"**Severity:** {severity.upper()}")
                    st.write(f"**Description:** {alert.get('description', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No threat alerts")
        
        with alert_tabs[2]:
            if vuln_alerts:
                for alert in vuln_alerts:
                    severity = alert.get("severity", "medium")
                    css_class = f"alert-{severity}"
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    st.write(f"**Type:** {alert.get('alert_type', 'unknown')}")
                    st.write(f"**Severity:** {severity.upper()}")
                    st.write(f"**Description:** {alert.get('description', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No vulnerability alerts")
        
        with alert_tabs[3]:
            if policy_alerts:
                for alert in policy_alerts:
                    severity = alert.get("severity", "medium")
                    css_class = f"alert-{severity}"
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                    st.write(f"**Type:** {alert.get('alert_type', 'unknown')}")
                    st.write(f"**Severity:** {severity.upper()}")
                    st.write(f"**Description:** {alert.get('description', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No policy alerts")
        
        # Incidents
        if incidents:
            st.subheader("🚨 Security Incidents")
            for incident in incidents:
                with st.expander(f"Incident {incident.get('incident_id', 'unknown')} - {incident.get('severity', 'unknown').upper()}"):
                    st.json(incident)
        
        # Export results
        st.divider()
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        with col1:
            json_str = json.dumps(result, indent=2, default=str)
            st.download_button(
                "Download JSON",
                json_str,
                file_name=f"security_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Create CSV from alerts
            if all_alerts:
                df = pd.DataFrame(all_alerts)
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    file_name=f"security_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

with tab4:
    st.header("ℹ️ About This System")
    
    st.markdown("""
    ### 🛡️ Cybersecurity Multi-Agent System
    
    A comprehensive cybersecurity monitoring system with multiple specialized AI agents that work together to protect systems, detect threats, and respond to incidents.
    
    #### 🤖 Agents
    
    1. **Log Monitor Agent** - Analyzes system and application logs in real-time
    2. **Threat Intelligence Agent** - Correlates threats with known attack patterns
    3. **Vulnerability Scanner Agent** - Identifies security weaknesses
    4. **Incident Response Agent** - Coordinates responses to security events
    5. **Policy Checker Agent** - Ensures compliance with security policies
    
    #### 🔧 Technology Stack
    
    - **Framework**: LangGraph for multi-agent orchestration
    - **UI**: Streamlit
    - **Hosting**: Hugging Face Spaces
    
    #### 📝 Usage
    
    1. Initialize the system from the sidebar
    2. Go to the "Analysis" tab
    3. Input your logs, system info, or threat indicators
    4. Click "Run Security Analysis"
    5. View results in the "Results" tab
    
    #### ⚠️ Note
    
    This is a demonstration system. For production use, integrate with real log sources, threat intelligence feeds, and security tools.
    
    #### 📚 Learn More
    
    Check the repository for detailed documentation and examples.
    """)
    
    st.divider()
    st.markdown("**Built with ❤️ using LangGraph and Streamlit**")

