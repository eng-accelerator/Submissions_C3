import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from core.graph import create_graph
from agents.cookbook import create_vector_store

import yaml

# Load environment variables
load_dotenv()

# Load Config File
config = {}
if os.path.exists("config.yaml"):
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f) or {}

st.set_page_config(page_title="AI DevOps Incident Analyst", layout="wide")

st.title("🤖 AI DevOps Incident Analyst")
st.markdown("Automated incident analysis, remediation, and reporting.")

# Helper to get config value
def get_conf(section, key, env_var):
    val = config.get(section, {}).get(key, "")
    if not val:
        val = os.getenv(env_var, "")
    return val

# Sidebar for Configuration & Inputs
with st.sidebar:
    st.subheader("Input Data")
    uploaded_log = st.file_uploader("Upload DevOps Log", type=["log", "txt", "json"])
    uploaded_cookbook = st.file_uploader("Upload Cookbook/Doc", type=["pdf", "txt", "md"])
    
    start_btn = st.button("Start Analysis")
    
    st.divider()
    
    st.header("Configuration")
    
    openrouter_key = st.text_input("OpenRouter API Key", type="password", value=os.getenv("OPENROUTER_API_KEY", ""))
    
    
    # Integrations loaded from config/env
    jira_url = get_conf("jira", "url", "JIRA_URL")
    jira_user = get_conf("jira", "user", "JIRA_USER")
    jira_token = get_conf("jira", "api_token", "JIRA_API_TOKEN")
    jira_project = get_conf("jira", "project_key", "JIRA_PROJECT_KEY")
    jira_issue_type = get_conf("jira", "issue_type", "JIRA_ISSUE_TYPE") or "Task"
    
    slack_webhook = get_conf("slack", "webhook_url", "SLACK_WEBHOOK_URL")
    
    st.divider()

# Main Layout
st.subheader("Analysis Dashboard")
status_container = st.container()
result_container = st.container()

if start_btn:
    if not openrouter_key:
        st.error("Please provide an OpenRouter API Key.")
    elif not uploaded_log:
        st.error("Please upload a log file.")
    else:
        status_container.info("Initializing Agent Workflow...")
        
        # Read Log
        log_content = uploaded_log.getvalue().decode("utf-8")
        
        # Process Cookbook if exists
        vector_store = None
        if uploaded_cookbook:
            status_container.info("Indexing Cookbook...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_cookbook.name.split('.')[-1]}") as tmp:
                tmp.write(uploaded_cookbook.getvalue())
                tmp_path = tmp.name
            
            try:
                vector_store = create_vector_store(tmp_path, openrouter_key)
            except Exception as e:
                st.error(f"Error processing cookbook: {e}")
            finally:
                os.unlink(tmp_path)
                
        # Build Graph
        jira_config = {
            "url": jira_url, 
            "user": jira_user, 
            "token": jira_token,
            "project_key": jira_project,
            "issue_type": jira_issue_type
        }
        app = create_graph(openrouter_key, jira_config, slack_webhook, vector_store)
        
        # Run Graph
        initial_state = {"log_data": log_content, "messages": []}
        status_text = status_container.empty()
        
        try:
             # Streaming execution events could be added here for better UX
             result = app.invoke(initial_state)
             
             status_text.success("Analysis Complete!")
             
             with result_container:
                 # st.subheader("Analysis Results")
                 # st.json(result.get("analysis_results"))
                 
                 st.subheader("Recommended Remediation")
                 st.markdown(result.get("remediation_plan"))
                 
                 st.subheader("Actions Taken")
                 col_a, col_b = st.columns(2)
                 col_a.metric("JIRA Ticket", result.get("jira_ticket_key"))
                 col_b.metric("Slack Notification", "Sent" if result.get("slack_sent") else "Failed")
                 
                 errors = result.get("errors", [])
                 if errors:
                     st.error("Workflow Errors:")
                     for err in errors:
                         st.write(f"- {err}")
                 
        except Exception as e:
            st.error(f"Workflow Error: {e}")
