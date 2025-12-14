from langgraph.graph import StateGraph, END
from core.state import AgentState
from agents.log_reader import log_reader_agent
from agents.cookbook import cookbook_agent, create_vector_store
from agents.remediation import remediation_agent
from agents.jira_agent import jira_agent
from agents.notification import notification_agent
import functools

def create_graph(api_key: str, jira_config: dict, slack_webhook: str, vector_store=None):
    """
    Constructs the multi-agent workflow graph.
    """
    workflow = StateGraph(AgentState)
    
    # 1. Log Analysis Node
    workflow.add_node("log_reader", functools.partial(log_reader_agent, api_key=api_key))
    
    # 2. Cookbook Retrieval Node
    # Note: vector_store must be created before running graph if cookbook is present
    if vector_store:
        workflow.add_node("cookbook", functools.partial(cookbook_agent, api_key=api_key, vector_store=vector_store))
    else:
        # Pass-through if no cookbook
        workflow.add_node("cookbook", lambda state: {"cookbook_context": "No cookbook provided."})

    # 3. Remediation Node
    workflow.add_node("remediation", functools.partial(remediation_agent, api_key=api_key))
    
    # 4. JIRA Node
    workflow.add_node("jira", functools.partial(jira_agent, jira_config=jira_config))
    
    # 5. Notification Node
    workflow.add_node("notification", functools.partial(notification_agent, webhook_url=slack_webhook))

    # Define Edges
    workflow.set_entry_point("log_reader")
    workflow.add_edge("log_reader", "cookbook")
    workflow.add_edge("cookbook", "remediation")
    workflow.add_edge("remediation", "jira")
    workflow.add_edge("jira", "notification")
    workflow.add_edge("notification", END)
    
    return workflow.compile()
