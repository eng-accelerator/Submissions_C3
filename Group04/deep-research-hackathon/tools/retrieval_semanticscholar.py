
import requests
from typing import List, Optional
from core.schema import Source

def search_semanticscholar(query: str, max_results: int = 5, api_key: Optional[str] = None) -> List[Source]:
    """
    Searches Semantic Scholar Graph API.
    Docs: https://api.semanticscholar.org/graph/v1
    """
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    fields = "paperId,title,abstract,venue,year,authors,citationCount,openAccessPdf,externalIds"
    
    params = {
        'query': query,
        'limit': max_results,
        'fields': fields
    }
    
    headers = {}
    if api_key:
        headers['x-api-key'] = api_key
        
    try:
        resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        
        if resp.status_code == 403:
            print("Semantic Scholar: API Key Invalid or Missing permissions.")
            return []
            
        data = resp.json()
        sources = []
        
        for item in data.get('data', []):
            paper_id = item.get('paperId')
            title = item.get('title', 'Untitled')
            year = item.get('year')
            venue = item.get('venue') or "Unknown Venue"
            abstract = item.get('abstract')
            citations = item.get('citationCount', 0)
            
            # Authors
            authors_list = item.get('authors', [])
            authors = [a.get('name') for a in authors_list]
            
            # Links
            pdf_data = item.get('openAccessPdf') or {}
            pdf_url = pdf_data.get('url')
            
            # DOI
            ext_ids = item.get('externalIds') or {}
            doi = ext_ids.get('DOI')
            
            # URL
            url = pdf_url or f"https://www.semanticscholar.org/paper/{paper_id}"
            if doi:
                url = f"https://doi.org/{doi}"
                
            snippet = abstract if abstract else f"Title: {title}. Venue: {venue}. Year: {year}."
            
            source = Source(
                id=f"s2_{paper_id}",
                title=title,
                url=url,
                snippet=snippet[:1000] if snippet else "",
                domain="semanticscholar.org",
                date=str(year) if year else "Unknown",
                year=year,
                authors=authors[:5],
                venue=venue,
                citations=citations,
                doi=doi,
                pdf_url=pdf_url,
                abstract=abstract,
                credibility_score=90, # High credibility
                credibility_reason=f"Semantic Scholar ({venue})"
            )
            sources.append(source)
            
        return sources

    except Exception as e:
        print(f"Semantic Scholar Search Failed: {e}")
        return []
