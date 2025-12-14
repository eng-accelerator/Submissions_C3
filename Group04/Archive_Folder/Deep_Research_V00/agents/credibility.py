from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from modules.llm_factory import LLMFactory

class CredibilityAgent:
    """
    Evaluates and scores the credibility of sources.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.0)

    def evaluate_sources(self, sources: list) -> list:
        """
        Assign confidence scores to sources.
        """
        if not self.llm:
            return []

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Fact Checker.
            Evaluate the credibility of the following sources.
            Assign a score (0-100) based on authority, recency, and domain relevance.
            
            Output a JSON list of objects: {{"source": "url/name", "score": int, "reason": "str"}}
            """),
            ("human", "Sources: {sources}")
        ])

        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            scores = chain.invoke({"sources": str(sources)})
            return scores
        except Exception:
            return []
