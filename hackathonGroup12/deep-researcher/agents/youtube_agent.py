# agents/youtube_agent.py

import sys
from pathlib import Path
from typing import Dict

# --------------------------------------------------
# Ensure project root is in path
# --------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from youtube_utils import (
    search_youtube_videos,
    TranscriptFetcher,
    TranscriptSummarizer,
)

# --------------------------------------------------
# YouTube Agent Node
# --------------------------------------------------

def youtube_agent_node(
    state: Dict,
    openrouter_api_key: str,
    youtube_api_key: str,
) -> Dict:
    """
    LangGraph node:
    - Searches YouTube
    - Fetches transcripts
    - Summarizes videos
    - Stores results in state["youtube_results"]
    """

    query = state.get("query", "")
    results = []

    if not query or not youtube_api_key or not openrouter_api_key:
        state["youtube_results"] = results
        return state

    fetcher = TranscriptFetcher()
    summarizer = TranscriptSummarizer(openrouter_api_key)

    try:
        videos = search_youtube_videos(
            youtube_api_key,
            query,
            max_results=2,
        )

        for video in videos:
            transcript_path = fetcher.fetch_transcript(video["url"])
            summary = summarizer.summarize(
                transcript_path,
                video["title"],
            )

            results.append({
                "video": video,
                "summary": summary,
            })

    except Exception as e:
        results.append({
            "error": str(e),
        })

    state["youtube_results"] = results
    return state
