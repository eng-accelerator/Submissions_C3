import requests
from typing import List
from core.schema import Source
from core.api_registry import APIRegistry

def search_github(query: str, filters: dict = None, max_results: int = 10) -> List[Source]:
    """
    Search GitHub for repositories or issues.
    Filters:
        - github_type: repositories, issues, code (default: repositories)
    """
    if filters is None: filters = {}
    
    token = APIRegistry.get_key("github_token")
    headers = {'Accept': 'application/vnd.github.v3+json'}
    if token:
        headers['Authorization'] = f'token {token}'
    
    sources = []
    base_url = "https://api.github.com/search/repositories"
    
    # Simple logic: Default to repo search, extended can be issues
    search_type = filters.get("github_type", "repositories") 
    if search_type == "issues":
        base_url = "https://api.github.com/search/issues"
    
    params = {
        'q': query,
        'per_page': max_results,
        'sort': 'stars' # Default sort
    }

    try:
        resp = requests.get(base_url, headers=headers, params=params)
        if resp.status_code == 200:
            items = resp.json().get('items', [])
            for item in items:
                # Handle diff structures for repo vs issue
                title = item.get('title') if search_type == 'issues' else item.get('full_name')
                url = item.get('html_url')
                snippet = item.get('body') if search_type == 'issues' else item.get('description')
                
                s = Source(
                    id=f"gh_{item.get('id')}",
                    title=title or "No Title",
                    url=url,
                    snippet=str(snippet)[:500] if snippet else "No description",
                    domain="github.com",
                    date=item.get('created_at', ''),
                    credibility_score=60, # Developer signal
                    credibility_reason="Official Repo/Issue",
                    metadata={
                        "stars": item.get('stargazers_count'),
                        "resource_type": "developer"
                    }
                )
                sources.append(s)
        elif resp.status_code == 403:
            print("GitHub Rate Limit Exceeded (consider adding token).")
        else:
            print(f"GitHub API Error: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"GitHub Search Error: {e}")

    return sources
