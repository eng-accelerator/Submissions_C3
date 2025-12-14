from typing import List, Dict, Optional, Literal, Any
from pydantic import BaseModel, Field

# --- Core Entities ---

class Source(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    domain: str
    date: str
    credibility_score: int = 0
    credibility_reason: str = "Not analyzed"
    
    # Academic Metadata
    authors: List[str] = Field(default_factory=list)
    venue: Optional[str] = None
    year: Optional[int] = None
    pdf_url: Optional[str] = None
    doi: Optional[str] = None
    citations: Optional[int] = None
    abstract: Optional[str] = None
    # Generic Metadata (for Reddit scores, YouTube views, etc.)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Claim(BaseModel):
    id: str
    text: str
    status: Literal["Verified", "Disputed", "Uncertain"]
    citation_source_ids: List[str] = Field(default_factory=list)
    confidence_score: int = 0
    notes: str = ""

class Contradiction(BaseModel):
    id: str
    claim_a_id: str
    claim_b_id: str
    description: str
    severity: Literal["High", "Medium", "Low"]

class AgentLog(BaseModel):
    agent_name: str
    message: str
    timestamp: float

# --- LangGraph State ---

class ResearchState(BaseModel):
    # Inputs
    question: str
    depth: Literal["Fast", "Balanced", "Deep"] = "Balanced"
    source_types: List[str] = Field(default_factory=lambda: ["Web"])
    resource_groups: List[str] = Field(default_factory=lambda: ["Web"]) # e.g. ["Academic", "Community"]
    source_filters: Dict[str, Any] = Field(default_factory=dict) # e.g. {"reddit_subreddits": "marketing", "youtube_sort": "relevance"}
    prefer_recent: bool = False
    template: str = "Research Report"
    demo_mode: bool = False
    
    # Context
    research_objective: str = "Learn"
    claim_to_validate: Optional[str] = None
    target_audience: str = "General"

    confidence_score_target: str = "Medium"
    time_sensitivity: str = "Evergreen"
    geography: str = "Global"
    
    # New V2 Fields
    domain: str = "General" # Finance, Medical, Academic, etc.
    research_context: Dict[str, Any] = Field(default_factory=dict) # Wizard inputs
    evaluation_mode: str = "Standard" # Standard, Judge, Debate
    judge_scorecard: Dict[str, Any] = Field(default_factory=dict)
    debate_transcript: List[Dict[str, Any]] = Field(default_factory=list)
    router_settings: Dict[str, Any] = Field(default_factory=dict)
    context_data: str = "" # Stores RAG/Multimodal context
    
    # Judge Mode
    feedback: Optional[str] = None
    review_count: int = 0
    
    # Constraints
    known_assumptions: str = ""
    source_exclusions: str = ""
    preferred_evidence_types: List[str] = Field(default_factory=list)

    # Process State
    plan: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    findings: Dict[str, str] = Field(default_factory=dict) # topic -> finding text

    # Analysis
    claims: List[Claim] = Field(default_factory=list)
    contradictions: List[Contradiction] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    
    # New Agent Outputs
    community_signals: List[str] = Field(default_factory=list) # from CommunitySignalAgent
    practical_steps: List[str] = Field(default_factory=list)   # from TutorialHowToAgent

    # Outputs
    report_md: str = ""
    templated_output: str = ""
    
    # Meta
    warnings: List[str] = Field(default_factory=list)
    logs: List[AgentLog] = Field(default_factory=list)
