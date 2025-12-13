from typing import List, Dict, Optional
import re
from config import Config
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import ArxivAPIWrapper, PubMedAPIWrapper
from langchain_community.tools.google_serper import GoogleSerperResults
from utils.logging import logger

class SearchTools:
    """
    Provides search capabilities with fallback mechanisms.
    Includes academic paper retrieval (arXiv, PubMed) and DOI resolution.
    """
    
    def __init__(self):
        self.arxiv_wrapper = ArxivAPIWrapper(top_k_results=3)
        self.pubmed_wrapper = PubMedAPIWrapper(top_k_results=3)
    
    @staticmethod
    def get_search_tool():
        """
        Returns the best available search tool. 
        Priority: Google Serper > Tavily > DuckDuckGo
        """
        serper_key = Config.get_api_key("serper")
        tavily_key = Config.get_api_key("tavily")
        
        if serper_key:
            logger.info("Initializing Google Serper Search Tool")
            return GoogleSerperResults(serper_api_key=serper_key, k=5)
        elif tavily_key:
            logger.info("Initializing Tavily Search Tool")
            return TavilySearchResults(
                tavily_api_key=tavily_key,
                max_results=5
            )
        else:
            logger.warning("No premium search API key found. Falling back to DuckDuckGo.")
            return DuckDuckGoSearchRun()
    
    @staticmethod
    def is_doi(query: str) -> bool:
        """Check if query is a DOI."""
        doi_pattern = r'10\.\d{4,}/[-._;()/:a-zA-Z0-9]+'
        return bool(re.search(doi_pattern, query))
    
    @staticmethod
    def is_arxiv_id(query: str) -> bool:
        """Check if query is an arXiv identifier."""
        arxiv_pattern = r'\d{4}\.\d{4,5}(v\d+)?|arxiv:\d{4}\.\d{4,5}(v\d+)?'
        return bool(re.search(arxiv_pattern, query, re.IGNORECASE))
    
    def resolve_doi(self, doi: str) -> Optional[Dict]:
        """
        Resolve a DOI to get paper information.
        Uses arXiv/PubMed APIs when possible, otherwise web search.
        """
        try:
            # Try to extract clean DOI
            doi_match = re.search(r'10\.\d{4,}/[-._;()/:a-zA-Z0-9]+', doi)
            if not doi_match:
                return None
            
            clean_doi = doi_match.group(0)
            logger.info(f"Resolving DOI: {clean_doi}")
            
            # Try arXiv first (many papers have both DOI and arXiv ID)
            # For now, use web search to find the paper
            # In production, you'd use CrossRef API or similar
            web_results = self.search(f"DOI {clean_doi}")
            if web_results:
                return {
                    "content": web_results[0].get("content", ""),
                    "source": f"DOI: {clean_doi}",
                    "url": f"https://doi.org/{clean_doi}",
                    "type": "academic",
                    "doi": clean_doi
                }
        except Exception as e:
            logger.error(f"DOI resolution failed: {e}")
        return None
    
    def search_academic(self, query: str) -> List[Dict]:
        """
        Search academic papers from arXiv and PubMed.
        """
        results = []
        
        try:
            # Search arXiv
            logger.info(f"Searching arXiv for: {query}")
            arxiv_docs = self.arxiv_wrapper.get_summaries_as_docs(query)
            for doc in arxiv_docs:
                results.append({
                    "content": doc.page_content,
                    "source": doc.metadata.get("Entry ID", "arXiv"),
                    "url": doc.metadata.get("Entry ID", ""),
                    "type": "academic",
                    "source_type": "arxiv",
                    "title": doc.metadata.get("Title", ""),
                    "authors": doc.metadata.get("Authors", ""),
                    "published": doc.metadata.get("Published", "")
                })
        except Exception as e:
            logger.error(f"arXiv search failed: {e}")
        
        try:
            # Search PubMed (for biomedical papers)
            logger.info(f"Searching PubMed for: {query}")
            pubmed_results = self.pubmed_wrapper.run(query)
            if pubmed_results and "No good PubMed Result" not in pubmed_results:
                # PubMed returns formatted text, parse it
                results.append({
                    "content": pubmed_results,
                    "source": "PubMed",
                    "url": "",
                    "type": "academic",
                    "source_type": "pubmed"
                })
        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
        
        return results

    def search(self, query: str, include_academic: bool = True) -> List[Dict]:
        """
        Execute a comprehensive search including web, academic papers, and DOI resolution.
        
        Args:
            query: Search query or DOI
            include_academic: Whether to include academic paper searches
        """
        results = []
        
        # Check if it's a DOI
        if self.is_doi(query):
            doi_result = self.resolve_doi(query)
            if doi_result:
                results.append(doi_result)
                return results
        
        # Check if it's an arXiv ID
        if self.is_arxiv_id(query):
            try:
                arxiv_docs = self.arxiv_wrapper.get_summaries_as_docs(query)
                for doc in arxiv_docs:
                    results.append({
                        "content": doc.page_content,
                        "source": doc.metadata.get("Entry ID", "arXiv"),
                        "url": f"https://arxiv.org/abs/{doc.metadata.get('Entry ID', '')}",
                        "type": "academic",
                        "source_type": "arxiv",
                        "title": doc.metadata.get("Title", ""),
                        "authors": doc.metadata.get("Authors", "")
                    })
                if results:
                    return results
            except Exception as e:
                logger.error(f"arXiv ID resolution failed: {e}")
        
        # Academic paper search
        if include_academic:
            academic_results = self.search_academic(query)
            results.extend(academic_results)
        
        # Web search
        tool = SearchTools.get_search_tool()
        try:
            web_results = tool.invoke(query)
            
            # Normalize web results
            if isinstance(web_results, str):
                results.append({
                    "content": web_results,
                    "source": "DuckDuckGo Search",
                    "url": "",
                    "type": "web"
                })
            elif isinstance(web_results, list):
                for res in web_results:
                    if isinstance(res, dict):
                        results.append({
                            "content": res.get("content", res.get("snippet", "")),
                            "source": res.get("url", res.get("link", "Unknown")),
                            "url": res.get("url", res.get("link", "")),
                            "type": "web"
                        })
                    else:
                        results.append({
                            "content": str(res),
                            "source": "Web Search",
                            "url": "",
                            "type": "web"
                        })
        except Exception as e:
            logger.error(f"Web search failed: {e}")
        
        return results if results else [{
            "content": f"Search failed for query '{query}'",
            "source": "Error",
            "url": "",
            "type": "error"
        }]
