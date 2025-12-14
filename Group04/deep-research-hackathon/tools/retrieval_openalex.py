
import requests
import datetime
from typing import List
from core.schema import Source

def search_openalex(query: str, max_results: int = 5) -> List[Source]:
    """
    Searches OpenAlex API.
    Docs: https://docs.openalex.org/
    """
    base_url = "https://api.openalex.org/works"
    
    # Filter for works that have a title and abstract to be useful
    params = {
        'search': query,
        'per-page': max_results,
        'filter': 'has_abstract:true',
        'sort': 'relevance_score:desc'
    }
    
    try:
        # Polite pool etiquette: Use email if possible, but strict rule says NO API KEYS. 
        # OpenAlex allows anonymous usage but slower/rate-limited.
        headers = {
            'User-Agent': 'DeepTraceResearcher/1.0 (mailto:researcher@example.com)' 
        }
        
        resp = requests.get(base_url, params=params, headers=headers, timeout=10)
        data = resp.json()
        
        sources = []
        
        results = data.get('results', [])
        for item in results:
            # ID: https://openalex.org/W2741809807 -> W2741809807
            oa_id = item.get('id', '').split('/')[-1]
            title = item.get('title', 'Untitled')
            
            # Pub Date
            pub_date = item.get('publication_date', '') # YYYY-MM-DD
            year = item.get('publication_year')
            
            # Venue
            venue_obj = item.get('primary_location', {}).get('source', {})
            venue = venue_obj.get('display_name') if venue_obj else "Unknown Venue"
            
            # Authors
            authors_list = item.get('authorships', [])
            authors = [a.get('author', {}).get('display_name', 'Unknown') for a in authors_list]
            
            # Abstract (OpenAlex uses inverted index, we need to reconstruct or skip)
            # Actually, standard OpenAlex return inverted index. Reconstruction is expensive.
            # We will use snippet from display_name or similar if abstract is messy, 
            # Or use 'abtract_inverted_index' if present but complex.
            # Simplified: Use title + venue as snippet if abstract is hard. 
            # Actually OpenAlex API usually requires extra work for abstract text. 
            # We will try to rely on 'title' and other metadata for MVP context. 
            snippet = f"Title: {title}. Venue: {venue}. Published: {pub_date}."
            
            # Citations
            citations = item.get('cited_by_count', 0)
            
            # DOI
            doi = item.get('doi') # https://doi.org/10.123...
            
            # URL
            url = doi or item.get('id')
            
            # Open Access PDF
            pdf_url = item.get('open_access', {}).get('oa_url')
            
            source = Source(
                id=f"openalex_{oa_id}",
                title=title,
                url=url,
                snippet=snippet,
                domain="openalex.org",
                date=pub_date,
                year=year,
                authors=authors[:5], # First 5
                venue=venue,
                citations=citations,
                doi=doi,
                pdf_url=pdf_url,
                abstract=None, # Inverted index too complex for this snippet
                credibility_score=85, # Generally high
                credibility_reason=f"OpenAlex Work ({venue})"
            )
            sources.append(source)
            
        return sources

    except Exception as e:
        print(f"OpenAlex Search Failed: {e}")
        return []
