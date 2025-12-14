from typing import TypedDict, List, Dict, Optional, Any
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State object passed between agents in LangGraph"""
    
    # Input
    logs: str
    chat_history: List[BaseMessage]
    
    # Agent outputs
    classified_incidents: Optional[List[Dict]]
    incident_summary: Optional[Dict]
    remediations: Optional[List[Dict]]
    notifications: Optional[List[Dict]]
    cookbooks: Optional[List[Dict]]
    jira_tickets: Optional[List[Dict]]
    
    # RAG context
    similar_historical_incidents: Optional[List[Dict]]
    
    # Execution metadata
    execution_plan: Optional[Dict]
    errors: List[str]
    agent_outputs: Dict[str, Any]