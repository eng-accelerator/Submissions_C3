from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from modules.llm_factory import LLMFactory
from utils.logging import logger

class ResearchScope(BaseModel):
    scope: str = Field(description="The defined boundaries of the research.")
    assumptions: List[str] = Field(description="List of assumed facts or conditions.")
    limitations: List[str] = Field(description="Known constraints of the research.")
    time_horizon: str = Field(description="The time period covered by the research (e.g. 'Last 5 years').")

class SubQuery(BaseModel):
    query: str = Field(description="A specific search query to answer part of the main objective.")
    source_type: str = Field(description="Type of source to prioritize (e.g., 'academic', 'news', 'general').")
    domain: str = Field(description="Domain classification: 'policy', 'tech', 'geopolitics', 'market', 'scientific', 'business', 'other'.")
    assigned_agent: str = Field(description="Which agent should handle this query: 'retriever', 'analyst', 'insight', or 'all'.")
    rationale: str = Field(description="Why this query is necessary.")

class ResearchPlan(BaseModel):
    main_objective: str = Field(description="The specific goal of the research.")
    primary_domains: List[str] = Field(description="List of primary domains identified: policy, tech, geopolitics, market, scientific, business, etc.")
    scope_and_assumptions: ResearchScope = Field(description="Defined scope, assumptions, and limitations.")
    sub_queries: List[SubQuery] = Field(description="Ordered list of search queries to execute with domain and agent assignments.")
    required_information: List[str] = Field(description="Key pieces of information needed.")
    agent_routing: Dict[str, List[str]] = Field(description="Mapping of which queries go to which agents.")

class PlannerAgent:
    """
    Analyzes the user request and creates a structured research plan.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.1)
        self.parser = PydanticOutputParser(pydantic_object=ResearchPlan)

    def create_plan(self, user_query: str, discipline: str, context_files: List[str] = []) -> ResearchPlan:
        """
        Generates a research plan based on the query and discipline.
        """
        if not self.llm:
            logger.error("LLM not initialized for Planner Agent.")
            return None

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Query Understanding Agent and Lead Research Planner specializing in {discipline}.
            Your goal is to break down a complex user query into a structured research plan with domain identification and agent routing.
            
            You must:
            1. Identify PRIMARY DOMAINS: Classify the query into domains such as:
               - policy (government, regulations, laws)
               - tech (technology, software, hardware, AI)
               - geopolitics (international relations, conflicts, diplomacy)
               - market (economics, finance, business, stocks)
               - scientific (research, academic, studies)
               - business (companies, strategies, markets)
               - other (specify)
            
            2. Break the query into smaller, actionable sub-queries.
            
            3. For EACH sub-query:
               - Identify its DOMAIN
               - Assign which AGENT should handle it:
                 * 'retriever' - for information gathering
                 * 'analyst' - for critical analysis
                 * 'insight' - for deep reasoning
                 * 'all' - for comprehensive handling
            
            4. Define a clear Research Scope with assumptions and limitations.
            
            5. Create agent_routing mapping showing which queries go to which agents.
            
            Context from files: {context_overview}
            
            Output must be valid JSON adhering to the schema.
            """),
            ("human", "{query}")
        ])

        chain = prompt | self.llm | self.parser
        
        context_str = ", ".join(context_files) if context_files else "None"
        
        try:
            plan = chain.invoke({
                "discipline": discipline,
                "context_overview": context_str,
                "query": user_query
            })
            logger.info(f"Plan created: {len(plan.sub_queries)} sub-queries.")
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            return None
