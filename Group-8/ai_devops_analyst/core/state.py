from typing import List, Dict, Any, Optional, TypedDict
import operator
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Represents the state of the multi-agent system.
    """
    messages: List[BaseMessage]
    log_data: Optional[str]
    cookbook_context: Optional[str]
    analysis_results: Optional[Dict[str, Any]]
    remediation_plan: Optional[str]
    jira_ticket_key: Optional[str]
    slack_sent: bool
    errors: List[str]
