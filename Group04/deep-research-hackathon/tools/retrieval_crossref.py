
import requests
import datetime
from typing import List
from core.schema import Source

def search_crossref(query: str, max_results: int = 5) -> List[Source]:
    """
    Searches Crossref API.
    Docs: https://github.com/CrossRef/rest-api-doc
    """
    base_url = "https://api.crossref.org/works"
    
    params = {
        'query.bibliographic': query,
        'rows': max_results,
        'sort': 'score',
        'order': 'desc'
    }
    
    try:
        # Polite headers recommended by Crossref
        headers = {
            'User-Agent': 'DeepTraceResearcher/1.0 (mailto:researcher@example.com)' 
        }
        
        resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        sources = []
        
        items = data.get('message', {}).get('items', [])
        for item in items:
            title_list = item.get('title', [])
            title = title_list[0] if title_list else "Untitled"
            
            # DOI
            doi = item.get('DOI')
            url = item.get('URL') or f"https://doi.org/{doi}"
            
            # Date
            published = item.get('created', {})
            date_parts = published.get('date-parts', [[None]])
            year = date_parts[0][0]
            date_str = str(year) if year else "Unknown"
            
            # Venue
            venue_list = item.get('container-title', [])
            venue = venue_list[0] if venue_list else "Unknown Venue"
            
            # Authors
            authors_list = item.get('author', [])
            authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in authors_list]
            
            # Citations (is-referenced-by-count)
            citations = item.get('is-referenced-by-count', 0)
            
            # Abstract often missing in Crossref standard search, snippet constructed
            snippet = f"DOI: {doi}. Venue: {venue}. Citations: {citations}."
            
            source = Source(
                id=f"crossref_{doi.replace('/', '_') if doi else 'unknown'}",
                title=title,
                url=url,
                snippet=snippet,
                domain="crossref.org",
                date=date_str,
                year=year,
                authors=authors[:5],
                venue=venue,
                citations=citations,
                doi=doi,
                abstract=None,
                credibility_score=75,
                credibility_reason=f"Crossref Record ({venue})"
            )
            sources.append(source)
            
        return sources

    except Exception as e:
        print(f"Crossref Search Failed: {e}")
        return []
