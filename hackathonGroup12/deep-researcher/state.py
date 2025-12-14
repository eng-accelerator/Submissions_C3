# state.py
from typing import TypedDict, Optional, List, Dict

class ResearchState(TypedDict, total=False):
    query: str
    youtube_results: Optional[List[Dict]]   # 🔹 ADD THIS
    retrieved: Optional[str]
    structured: Optional[str]
    analysis: Optional[str]
    factchecked: Optional[str]
    expert: Optional[str]
    critique: Optional[str]
    insights: Optional[str]
    report: Optional[str]
