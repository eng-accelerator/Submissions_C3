from langgraph.graph import StateGraph, END
from orchestration.state import AgentState
from agents.log_classifier import LogClassifierAgent
from agents.remediation_agent import RemediationAgent
from agents.notification_agent import NotificationAgent
from agents.cookbook_agent import CookbookAgent
from agents.jira_agent import JiraAgent
from utils.rag_engine import RAGEngine
from utils.openrouter_client import OpenRouterClient
from typing import Dict, Any, List

class IncidentAnalysisGraph:
    """LangGraph orchestrator for multi-agent workflow"""
    
    def __init__(self, api_key: str, model: str, rag_engine: RAGEngine):
        self.client = OpenRouterClient(api_key)
        self.model = model
        # Pass API key to RAG engine for OpenAI embeddings
        if hasattr(rag_engine, 'openrouter_api_key') and not rag_engine.openrouter_api_key:
            rag_engine.openrouter_api_key = api_key
            rag_engine._initialize_embedding_method()  # Reinitialize with API key
        self.rag_engine = rag_engine
        
        # Initialize agents with OpenAI models
        self.log_classifier = LogClassifierAgent(self.client, self.model)
        self.remediation_agent = RemediationAgent(self.client, self.model)
        self.notification_agent = NotificationAgent(self.client, self.model)
        self.cookbook_agent = CookbookAgent(self.client, self.model)
        self.jira_agent = JiraAgent(self.client, self.model)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Construct the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("rag_retrieval", self.rag_retrieval_node)
        workflow.add_node("classify", self.classify_node)
        workflow.add_node("remediate", self.remediate_node)
        workflow.add_node("notify", self.notify_node)
        workflow.add_node("cookbook", self.cookbook_node)
        workflow.add_node("jira", self.jira_node)
        
        # Define edges (workflow)
        workflow.set_entry_point("rag_retrieval")
        workflow.add_edge("rag_retrieval", "classify")
        workflow.add_edge("classify", "remediate")
        
        # After remediation, run notify, cookbook, and jira sequentially
        # (Sequential execution is fine for this use case)
        workflow.add_edge("remediate", "notify")
        workflow.add_edge("notify", "cookbook")
        workflow.add_edge("cookbook", "jira")
        workflow.add_edge("jira", END)
        
        return workflow.compile()
    
    def rag_retrieval_node(self, state: AgentState) -> AgentState:
        """Retrieve similar historical incidents using LanceDB"""
        logs = state["logs"]
        similar = self.rag_engine.retrieve_similar_incidents(logs, n_results=3)
        state["similar_historical_incidents"] = similar
        return state
    
    def classify_node(self, state: AgentState) -> AgentState:
        """Log classification node"""
        context = {
            "logs": state["logs"],
            "similar_historical_incidents": state.get("similar_historical_incidents", [])
        }
        result = self.log_classifier.execute(context)
        incidents = result.get("incidents", [])
        state["classified_incidents"] = incidents
        state["incident_summary"] = result.get("summary", {})
        state["agent_outputs"]["classifier"] = result
        
        # Index incidents for future RAG retrieval
        try:
            for incident in incidents:
                incident_id = incident.get("id", f"INC-{len(incidents)}")
                self.rag_engine.index_incident(incident_id, incident)
        except Exception as e:
            # Log but don't fail the workflow
            print(f"Warning: Failed to index incidents: {e}")
        
        return state
    
    def remediate_node(self, state: AgentState) -> AgentState:
        """Remediation node"""
        context = {
            "classified_incidents": state["classified_incidents"],
            "similar_historical_incidents": state.get("similar_historical_incidents", [])
        }
        result = self.remediation_agent.execute(context)
        state["remediations"] = result.get("remediations", [])
        state["agent_outputs"]["remediation"] = result
        return state
    
    def notify_node(self, state: AgentState) -> AgentState:
        """Notification node"""
        context = {
            "classified_incidents": state["classified_incidents"],
            "incident_summary": state["incident_summary"]
        }
        result = self.notification_agent.execute(context)
        state["notifications"] = result.get("notifications", [])
        state["agent_outputs"]["notification"] = result
        return state
    
    def cookbook_node(self, state: AgentState) -> AgentState:
        """Cookbook generation node"""
        context = {"remediations": state["remediations"]}
        result = self.cookbook_agent.execute(context)
        state["cookbooks"] = result.get("cookbooks", [])
        state["agent_outputs"]["cookbook"] = result
        return state
    
    def jira_node(self, state: AgentState) -> AgentState:
        """JIRA ticket creation node"""
        context = {
            "classified_incidents": state["classified_incidents"],
            "remediations": state["remediations"]
        }
        result = self.jira_agent.execute(context)
        state["jira_tickets"] = result.get("tickets", [])
        state["agent_outputs"]["jira"] = result
        return state
    
    def run(self, logs: str, chat_history: List = None) -> Dict[str, Any]:
        """Execute the complete workflow"""
        initial_state = AgentState(
            logs=logs,
            chat_history=chat_history or [],
            classified_incidents=None,
            incident_summary=None,
            remediations=None,
            notifications=None,
            cookbooks=None,
            jira_tickets=None,
            similar_historical_incidents=None,
            execution_plan=None,
            errors=[],
            agent_outputs={}
        )
        
        final_state = self.graph.invoke(initial_state)
        return final_state