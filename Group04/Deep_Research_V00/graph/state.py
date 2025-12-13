from typing import TypedDict, List, Dict, Any, Annotated, Optional
import operator

class AgentState(TypedDict, total=False):
    """
    Represents the shared state of the research graph.
    """
    # Inputs
    task: str
    discipline: str
    uploaded_files: List[Dict] # content of files
    
    # Planning
    plan: Optional[Dict] # ResearchPlan object as dict
    research_scope: Optional[Dict] # ResearchScope object as dict
    
    # Execution
    findings: Annotated[List[Dict], operator.add] # Accumulate findings
    insights: Optional[List[str]]
    hypotheses: Optional[List[str]] # Generated hypotheses
    reasoning_chains: Optional[List[str]] # Multi-hop reasoning chains
    connections: Optional[List[str]] # Connections between findings
    implications: Optional[List[str]] # Implications identified
    trends: Optional[List[str]] # Trends identified
    research_questions: Optional[List[str]] # Research questions for future investigation
    sources: Annotated[List[Dict], operator.add] # Accumulate sources with scores
    
    # Reflection
    reflection: Optional[Dict] # ReflectionValidation object
    iteration_count: int
    
    # Output
    final_report: Optional[str]
