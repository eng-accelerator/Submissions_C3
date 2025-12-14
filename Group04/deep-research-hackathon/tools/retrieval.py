import requests
from typing import List
from core.schema import Source
from core.api_registry import APIRegistry
from tools.retrieval_arxiv import search_arxiv
from tools.retrieval_openalex import search_openalex
from tools.retrieval_crossref import search_crossref
from tools.retrieval_reddit import search_reddit
from tools.retrieval_youtube import search_youtube
from tools.retrieval_github import search_github
from tools.retrieval_hackernews import search_hackernews

def retrieve_sources(query: str, state_filters: dict, resource_groups: List[str], source_types: List[str], max_results: int = 5, demo_mode: bool = False) -> List[Source]:
    """
    Unified entry point.
    Orchestrates searches based on resource_groups (e.g. Community, Video) and source_types.
    """
    all_sources = []
    
    # Removed Demo Mode check.
    # If no keys or sources, downstream agents will report error.

    # 1. Web Search (if Web group active)
    if "Web" in resource_groups:
        try:
            web_sources = search_web(query, max_results)
            all_sources.extend(web_sources)
        except Exception as e:
            print(f"Web Search error: {e}")

    # 2. Academic Search
    if "Academic" in resource_groups:
        academic_sources = search_academic(query, source_types, max_results)
        all_sources.extend(academic_sources)

    # 3. Community Search
    if "Community" in resource_groups:
        if "Reddit" in source_types:
            all_sources.extend(search_reddit(query, state_filters, max_results))
        if "Hacker News" in source_types:
            all_sources.extend(search_hackernews(query, state_filters, max_results))

    # 4. Video Search
    if "Video" in resource_groups and "YouTube" in source_types:
        all_sources.extend(search_youtube(query, state_filters, max_results))

    # 5. Developer Search
    if "Developer" in resource_groups and "GitHub" in source_types:
        all_sources.extend(search_github(query, state_filters, max_results))
        
    return _deduplicate(all_sources)

def search_web(query: str, max_results: int = 5) -> List[Source]:
    """
    Perform a web search using Tavily.
    """
    from tools.retrieval_perplexity import search_perplexity

    # 1. Try Tavily
    api_key = APIRegistry.get_key("search") 
    
    if not api_key:
        print("No Search (Tavily) API Key found.")
        
        # 2. Fallback to Perplexity (Native or OpenRouter)
        if APIRegistry.get_key("perplexity") or APIRegistry.get_key("openrouter_key"):
             print("Info: Falling back to Perplexity/OpenRouter for Web Search.")
             return search_perplexity(query, max_results)
             
        print("No Web Search fallback available. Returning empty list.")
        return []
    
    try:
        payload = {
            "api_key": api_key,
            "query": query,
            "search_depth": "basic",
            "include_domains": [],
            "exclude_domains": []
        }
        # Tavily API
        response = requests.post("https://api.tavily.com/search", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            sources = []
            for r in results:
                s = Source(
                    id=f"t_{hash(r['url'])}",
                    title=r.get('title', 'No Title'),
                    url=r.get('url', ''),
                    snippet=r.get('content', '')[:300] + "...",
                    domain=r.get('url', '').split('/')[2],
                    date="2024",
                    credibility_score=0
                )
                sources.append(s)
            return sources
        else:
            print(f"Tavily Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def search_academic(query: str, sources: List[str], max_results: int = 5) -> List[Source]:
    results = []
    
    if "arXiv" in sources:
        results.extend(search_arxiv(query, max_results))
        
    if "OpenAlex" in sources:
        results.extend(search_openalex(query, max_results))
        
    if "Crossref" in sources:
        results.extend(search_crossref(query, max_results))
        
    if "Semantic Scholar" in sources:
        # Check for key, optional
        s2_key = APIRegistry.get_key("semanticscholar")
        results.extend(search_semanticscholar(query, max_results, s2_key))
        
    return results

def _deduplicate(sources: List[Source]) -> List[Source]:
    """
    Deduplicate by DOI (strongest) then Title+Year (fuzzy).
    """
    seen_dois = set()
    seen_titles = set()
    unique = []
    
    for s in sources:
        # DOI Check
        if s.doi and s.doi in seen_dois:
            continue
            
        # Title Normalization (simple alphanumeric lower)
        norm_title = "".join(filter(str.isalnum, s.title.lower()))
        # Year check? Maybe just title is enough for loose dedup
        
        if norm_title in seen_titles:
            continue
            
        if s.doi:
            seen_dois.add(s.doi)
        seen_titles.add(norm_title)
        
        unique.append(s)
        
    return unique


