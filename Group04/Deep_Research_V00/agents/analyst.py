from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from modules.llm_factory import LLMFactory
from utils.logging import logger

class AnalystAgent:
    """
    Analyzes retrieved data to extract facts, identify contradictions, and summarize.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.2)

    def analyze(self, query: str, search_results: List[Dict]) -> Dict:
        """
        Synthesizes findings from search results.
        Returns a "Finding Pack" with structured contradictions, summaries, and validations.
        """
        if not self.llm:
            return {
                "summary": "LLM Error",
                "key_findings": [],
                "finding_pack": {
                    "summaries": [],
                    "contradictions": [],
                    "validations": [],
                    "missing_info": []
                }
            }

        # Format context
        context_text = ""
        for i, res in enumerate(search_results):
            if not isinstance(res, dict):
                continue
            source = res.get('source', 'Unknown Source')
            content = res.get('content', str(res))
            # Truncate for token limits
            content_preview = content[:2000] if isinstance(content, str) else str(content)[:2000]
            context_text += f"Source {i+1} ({source}):\n{content_preview}\n\n"

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Critical Research Analyst specializing in finding contradictions and validating information.
            Analyze the provided search results to answer the query: "{query}"
            
            Your primary tasks:
            1. Extract key facts and findings
            2. Identify CONTRADICTIONS between different sources (this is critical!)
            3. Validate claims by cross-referencing multiple sources
            4. Flag uncertainties and gaps in information
            5. Assess the reliability of each source
            
            Output a JSON with:
            - "summary": synthesized answer addressing the query
            - "key_findings": list of specific, validated facts
            - "contradictions": detailed list of conflicting information found between sources (include which sources contradict each other)
            - "validations": list of claims that were validated across multiple sources
            - "uncertainties": what is still unclear or requires more research
            - "source_reliability": assessment of each source's credibility
            - "sources_used": list of source indices used
            """),
            ("human", f"Context:\n{context_text}")
        ])

        chain = prompt | self.llm | StrOutputParser() # We'll parse the JSON in the workflow or use Pydantic here too
        # For robustness, let's just return text or use a parser if we have time. 
        # For now, let's keep it simple and assume the orchestrator handles the JSON parsing or we make it structured.
        
        # Actually, let's use a Pydantic parser for safety
        from langchain_core.output_parsers import JsonOutputParser
        chain = prompt | self.llm | JsonOutputParser()
        
        try:
            analysis = chain.invoke({"query": query})
            # Ensure we always return a dict with expected keys
            if not isinstance(analysis, dict):
                analysis = {"summary": str(analysis), "key_findings": []}
            # Ensure required keys exist
            if "summary" not in analysis:
                analysis["summary"] = ""
            if "key_findings" not in analysis:
                analysis["key_findings"] = []
            
            # Create Finding Pack structure
            finding_pack = {
                "summaries": [analysis.get("summary", "")],
                "contradictions": analysis.get("contradictions", []),
                "validations": analysis.get("validations", []),
                "missing_info": analysis.get("uncertainties", []),
                "source_reliability": analysis.get("source_reliability", {})
            }
            
            analysis["finding_pack"] = finding_pack
            return analysis
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "summary": f"Analysis error: {str(e)}",
                "key_findings": [],
                "finding_pack": {
                    "summaries": [],
                    "contradictions": [],
                    "validations": [],
                    "missing_info": []
                },
                "error": str(e)
            }
