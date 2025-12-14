import requests
from typing import List
from core.schema import Source
from core.api_registry import APIRegistry

def search_youtube(query: str, filters: dict = None, max_results: int = 10) -> List[Source]:
    """
    Search YouTube for videos.
    Filters:
        - youtube_sort: relevance, date, viewCount, rating, title, videoCount
        - youtube_duration: any, long, medium, short
    """
    if filters is None: filters = {}
    
    api_key = APIRegistry.get_key("youtube_api_key")
    if not api_key:
        print("⚠️ YouTube Search skipped: Missing API Key.")
        return []

    sources = []
    base_url = "https://www.googleapis.com/youtube/v3/search"
    
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'maxResults': max_results,
        'key': api_key,
        'order': filters.get("youtube_sort", "relevance"),
        'videoDuration': filters.get("youtube_duration", "any")
    }

    try:
        resp = requests.get(base_url, params=params)
        if resp.status_code == 200:
            items = resp.json().get('items', [])
            for item in items:
                snippet = item.get('snippet', {})
                video_id = item.get('id', {}).get('videoId')
                
                if video_id:
                    s = Source(
                        id=f"yt_{video_id}",
                        title=snippet.get('title', 'No Title'),
                        url=f"https://www.youtube.com/watch?v={video_id}",
                        snippet=snippet.get('description', ''),
                        domain="youtube.com",
                        date=snippet.get('publishedAt', ''),
                        credibility_score=30, # Moderate for video
                        credibility_reason="Video Content",
                        metadata={
                            "channel": snippet.get('channelTitle'),
                            "resource_type": "video"
                        }
                    )
                    sources.append(s)
        else:
            print(f"YouTube API Error: {resp.status_code} {resp.text}")

    except Exception as e:
        print(f"YouTube Search Error: {e}")

    return sources
