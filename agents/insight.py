from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from modules.llm_factory import LLMFactory
from utils.logging import logger

class InsightAgent:
    """
    Generates high-level insights and connects dots between findings.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.4)

    def generate_insights(self, research_findings: list, discipline: str) -> dict:
        """
        Produce deep insights and generate hypotheses from validated findings.
        Returns a dict with hypotheses, insights, implications, and research questions.
        """
        if not self.llm:
            return {
                "hypotheses": [],
                "insights": [],
                "reasoning_chains": [],
                "connections": [],
                "implications": [],
                "trends": [],
                "research_questions": []
            }

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Insight Generator Agent with multi-hop reasoning capabilities in {discipline}.
            
            You must perform MULTI-HOP REASONING:
            - Connect information across different sources and findings
            - Build logical chains of reasoning that link separate pieces of information
            - Identify relationships and patterns that aren't immediately obvious
            - Trace causal connections and dependencies
            
            Based on the provided research findings, you must:
            1. Generate testable HYPOTHESES that explain patterns in the data
            2. Perform MULTI-HOP REASONING to build connections between findings
            3. Identify implications and future trends
            4. Synthesize new knowledge from the findings
            5. Propose research questions that emerge from the analysis
            6. Build CONNECTIONS between pieces of information showing how they relate
            
            Don't just summarize; create new insights through multi-step reasoning.
            
            Output a JSON object with:
            - "hypotheses": list of testable hypotheses (e.g., ["Hypothesis 1: ...", "Hypothesis 2: ..."])
            - "insights": list of key insights and patterns
            - "reasoning_chains": list of multi-hop reasoning chains showing how findings connect (e.g., ["Finding A → leads to → Finding B → suggests → Insight C"])
            - "connections": list of relationships between different pieces of information
            - "implications": list of implications for the field
            - "trends": list of identified trends
            - "research_questions": list of new questions that should be investigated
            """),
            ("human", "Findings: {findings}")
        ])

        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            result = chain.invoke({
                "discipline": discipline,
                "findings": str(research_findings)
            })
            # Ensure all required keys exist
            if not isinstance(result, dict):
                result = {}
            return {
                "hypotheses": result.get("hypotheses", []),
                "insights": result.get("insights", []),
                "reasoning_chains": result.get("reasoning_chains", []),
                "connections": result.get("connections", []),
                "implications": result.get("implications", []),
                "trends": result.get("trends", []),
                "research_questions": result.get("research_questions", [])
            }
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {
                "hypotheses": [],
                "insights": ["Failed to generate insights."],
                "reasoning_chains": [],
                "connections": [],
                "implications": [],
                "trends": [],
                "research_questions": []
            }
