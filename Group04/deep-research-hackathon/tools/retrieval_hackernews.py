import requests
from typing import List
from core.schema import Source

def search_hackernews(query: str, filters: dict = None, max_results: int = 10) -> List[Source]:
    """
    Search Hacker News via Algolia.
    Filters:
        - hn_sort: search, search_by_date (default: search)
    """
    if filters is None: filters = {}
    
    sources = []
    base_url = "http://hn.algolia.com/api/v1/search"
    if filters.get("hn_sort") == "search_by_date":
        base_url = "http://hn.algolia.com/api/v1/search_by_date"
    
    params = {
        'query': query,
        'tags': 'story',
        'hitsPerPage': max_results
    }

    try:
        resp = requests.get(base_url, params=params)
        if resp.status_code == 200:
            hits = resp.json().get('hits', [])
            for hit in hits:
                s = Source(
                    id=f"hn_{hit.get('objectID')}",
                    title=hit.get('title', 'No Title'),
                    url=f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                    snippet=f"Points: {hit.get('points')} | Comments: {hit.get('num_comments')}",
                    domain="news.ycombinator.com",
                    date=hit.get('created_at', ''),
                    credibility_score=40,
                    credibility_reason="Tech Community Signal",
                    metadata={
                        "points": hit.get('points'),
                        "comments": hit.get('num_comments'),
                        "resource_type": "community"
                    }
                )
                sources.append(s)
        else:
            print(f"HN API Error: {resp.status_code}")

    except Exception as e:
        print(f"HN Search Error: {e}")

    return sources
