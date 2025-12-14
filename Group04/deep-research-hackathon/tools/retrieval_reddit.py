import requests
import time
from typing import List, Optional
from core.schema import Source
from core.api_registry import APIRegistry

def get_reddit_token(client_id: str, client_secret: str, user_agent: str) -> Optional[str]:
    """Exchanges client credentials for an access token."""
    try:
        auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
        data = {'grant_type': 'client_credentials'}
        headers = {'User-Agent': user_agent}
        resp = requests.post('https://www.reddit.com/api/v1/access_token',
                             auth=auth, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json().get('access_token')
    except Exception as e:
        print(f"Reddit Auth Error: {e}")
    return None

def search_reddit(query: str, filters: dict = None, max_results: int = 10) -> List[Source]:
    """
    Search Reddit for posts.
    Filters:
        - reddit_subreddits: comma-separated list of subreddits to restrict search to
        - reddit_sort: relevance, hot, top, new, comments (default: relevance)
        - reddit_time: hour, day, week, month, year, all (default: all)
    """
    if filters is None: filters = {}
    
    client_id = APIRegistry.get_key("reddit_client_id")
    client_secret = APIRegistry.get_key("reddit_client_secret")
    user_agent = APIRegistry.get_key("reddit_user_agent") or "DeepTrace/1.0"
    
    if not (client_id and client_secret):
        print("⚠️ Reddit Search skipped: Missing API Keys.")
        return []

    token = get_reddit_token(client_id, client_secret, user_agent)
    if not token:
        print("⚠️ Reddit Search skipped: Auth failed.")
        return []

    sources = []
    headers = {'Authorization': f'bearer {token}', 'User-Agent': user_agent}
    
    # Construct query
    # If subreddits provided, use `site:reddit.com/r/subreddit query` or restrict logic
    # Better: use /r/{subreddits}/search endpoint if restrictive, or global search with restrict_sr=on if single sub
    # To support multi-subreddit, /r/sub1+sub2/search is valid
    
    subreddits = filters.get("reddit_subreddits")
    base_url = "https://oauth.reddit.com"
    endpoint = "/search"
    
    params = {
        'q': query,
        'limit': max_results,
        'sort': filters.get("reddit_sort", "relevance"),
        't': filters.get("reddit_time", "all"),
        'type': 'link' # only posts, not subreddits/users
    }

    if subreddits:
        # Sanitization
        subs = "+".join([s.strip() for s in subreddits.split(",") if s.strip()])
        if subs:
            endpoint = f"/r/{subs}/search"
            params['restrict_sr'] = 'on'

    try:
        resp = requests.get(f"{base_url}{endpoint}", headers=headers, params=params)
        if resp.status_code == 200:
            data = resp.json()
            items = data.get('data', {}).get('children', [])
            
            for item in items:
                d = item['data']
                # Create source
                s = Source(
                    id=f"reddit_{d.get('id')}",
                    title=d.get('title', 'No Title'),
                    url=f"https://www.reddit.com{d.get('permalink')}",
                    snippet=d.get('selftext', '')[:500] or d.get('title'),
                    domain="reddit.com",
                    date=str(d.get('created_utc')), # Raw timestamp, could convert
                    credibility_score=20, # Low baseline for community
                    credibility_reason="Community Signal (Anecdotal)",
                    metadata={
                        "score": d.get('score'),
                        "num_comments": d.get('num_comments'),
                        "subreddit": d.get('subreddit'),
                        "resource_type": "community"
                    }
                )
                sources.append(s)
        else:
            print(f"Reddit API Error: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"Reddit Search Error: {e}")

    return sources
