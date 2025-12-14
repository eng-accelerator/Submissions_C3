from typing import List, Dict
from modules.llm_factory import LLMFactory
from tools.search_tools import SearchTools
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from utils.logging import logger

class RetrieverAgent:
    """
    Executes search queries and retrieves context from uploaded documents.
    """
    
    def __init__(self, model_provider="openai"):
        self.llm = LLMFactory.create_llm(model_provider, temperature=0.0)
        self.search_tool = SearchTools()  # Now an instance, not static

    def retrieve(self, sub_query: str, current_context: List[Dict], files_content: List[Dict]) -> List[Dict]:
        """
        Performs search and combines with file content.
        """
        results = []
        
        # 1. Comprehensive Search (Web + Academic Papers + DOI resolution)
        try:
            logger.info(f"Searching for: {sub_query}")
            # Search includes academic papers, web, and DOI resolution
            search_results = self.search_tool.search(sub_query, include_academic=True)
            # search_tool.search() returns List[Dict] with normalized format
            if isinstance(search_results, list):
                results.extend(search_results)
            else:
                # Fallback for unexpected types
                results.append({
                    "content": str(search_results),
                    "source": "Search (Fallback)",
                    "type": "web"
                })
        except Exception as e:
            logger.error(f"Search error: {e}")
            results.append({
                "content": f"Search error: {str(e)}",
                "source": "Error",
                "type": "error"
            })

        # 2. Local Document Search (Simple keyword match for hackathon speed)
        # In a real app, use VectorStore (Chroma/FAISS)
        keywords = sub_query.lower().split()
        for doc in files_content:
            score = 0
            doc_content_lower = doc['content'].lower()
            for kw in keywords:
                if kw in doc_content_lower:
                    score += 1
            
            if score > 0:
                # Retrieve chunks (simplified: just grab the doc or a window)
                # For this demo, we'll confirm relevance with LLM or just add the whole doc if small
                results.append({
                    "content": doc['content'], # In real PROD, chunk this!
                    "source": doc['source'],
                    "type": "file"
                })
        
        return results

    def relevance_filter(self, query: str, raw_results: List[Dict]) -> List[Dict]:
        """
        Uses LLM to filter irrelevant results.
        """
        if not self.llm or not raw_results:
            return raw_results

        # Quick check for relevance
        # This can be expensive, so we might skip for hackathon or do batched
        return raw_results # Optimization: Skip for speed unless results are huge
