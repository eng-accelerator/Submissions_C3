# youtube_utils.py

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Optional

from googleapiclient.discovery import build
from yt_dlp import YoutubeDL
from openai import OpenAI

# ==================================================
# CONFIG
# ==================================================

YOUTUBE_API_VERSION = "v3"
YOUTUBE_ORDER = "relevance"
DEFAULT_MAX_RESULTS = 2

OPENROUTER_MODEL = "openai/gpt-4o-mini"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_TIMEOUT = 120

SUMMARIZER_PROMPT = """
You are TechSummarizerAI.

Summarize the following YouTube transcript into structured JSON.

Format:
{
  "high_level_overview": "...",
  "technical_breakdown": [...],
  "insights": [...],
  "applications": [...]
}
"""

# ==================================================
# HELPERS
# ==================================================

def parse_duration(iso_duration: str) -> str:
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    match = re.match(pattern, iso_duration)

    if not match:
        return "Unknown"

    h, m, s = [int(x) if x else 0 for x in match.groups()]

    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


# ==================================================
# YOUTUBE SEARCH
# ==================================================

def search_youtube_videos(
    api_key: str,
    query: str,
    max_results: Optional[int] = None
) -> List[Dict]:

    max_results = max_results or DEFAULT_MAX_RESULTS

    youtube = build(
        "youtube",
        YOUTUBE_API_VERSION,
        developerKey=api_key
    )

    response = youtube.search().list(
        q=query,
        part="id,snippet",
        maxResults=max_results,
        type="video",
        order=YOUTUBE_ORDER
    ).execute()

    video_ids = [
        item["id"]["videoId"]
        for item in response.get("items", [])
        if "videoId" in item["id"]
    ]

    durations = {}
    if video_ids:
        details = youtube.videos().list(
            part="contentDetails",
            id=",".join(video_ids)
        ).execute()

        for item in details.get("items", []):
            durations[item["id"]] = item["contentDetails"]["duration"]

    videos = []
    for item in response.get("items", []):
        vid = item["id"]["videoId"]
        videos.append({
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "url": f"https://www.youtube.com/watch?v={vid}",
            "video_id": vid,
            "duration": parse_duration(durations.get(vid, "")),
        })

    return videos


# ==================================================
# TRANSCRIPT FETCHER
# ==================================================

class TranscriptFetcher:
    def __init__(self, language: str = "en"):
        self.language = language
        self.temp_dir = Path(f"yt_transcripts_{os.getpid()}")
        self.temp_dir.mkdir(exist_ok=True)

    def fetch_transcript(self, url: str) -> str:
        ydl_opts = {
            "skip_download": True,
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [self.language],
            "subtitlesformat": "srt",
            "outtmpl": str(self.temp_dir / "%(id)s.%(ext)s"),
            "ignoreerrors": True,
            "quiet": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_id = url.split("=")[-1]
        files = list(self.temp_dir.glob(f"{video_id}*.srt"))

        return str(files[0]) if files else ""


# ==================================================
# TRANSCRIPT SUMMARIZER
# ==================================================

class TranscriptSummarizer:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL
        )

    def summarize(self, transcript_path: str, title: str) -> Dict:
        if not transcript_path:
            return {"summary_text": "Transcript unavailable"}

        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        cleaned_lines = []
        for line in lines:
            if not line.strip():
                continue
            if line.isdigit():
                continue
            if "-->" in line:
                continue
            cleaned_lines.append(line)

        transcript_text = " ".join(cleaned_lines)

        prompt = f"""
Video Title: {title}

Transcript:
{transcript_text}
"""

        response = self.client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": SUMMARIZER_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            timeout=OPENROUTER_TIMEOUT,
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except Exception:
            return {"summary_text": content}
