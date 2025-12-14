from core.schema import ResearchState
from agents.base import log_agent_action

def credibility_node(state: ResearchState):
    """
    SourceCredibilityAgent:
    Review collected sources and assign scores.
    """
    updated_sources = []
    
    # Simple Heuristic for Demo
    high_trust_domains = ["gov", "edu", "arxiv.org", "nature.com"]
    
    for s in state.sources:
        # If score is 0 (unscored), apply heuristic
        if s.credibility_score == 0:
            if any(d in s.domain for d in high_trust_domains):
                s.credibility_score = 90
                s.credibility_reason = "High trust domain extension or known reputable source."
            else:
                s.credibility_score = 60
                s.credibility_reason = "General web source, verify independently."

        # Academic Adjustments
        if s.citations and s.citations > 50:
            s.credibility_score = min(100, s.credibility_score + 10)
            s.credibility_reason += " + Highly Cited"
        if s.venue and "Unknown" not in s.venue:
             s.credibility_score = min(100, s.credibility_score + 5)
             s.credibility_reason += f" + Venue ({s.venue})"
        if s.year and s.year < 2017:
             s.credibility_score = max(0, s.credibility_score - 5)
             s.credibility_reason += " - Older paper (<2017)"

        # Community / Video / Dev Adjustments
        meta = s.metadata
        rtype = meta.get("resource_type")
        
        if rtype == "community":
            # Baseline is usually lower (20-40), boost for engagement
            score = meta.get("score") or meta.get("points") or 0
            if score > 100:
                s.credibility_score = min(70, s.credibility_score + 20)
                s.credibility_reason += " + High Engagement (Signal)"
        
        elif rtype == "video":
            views = meta.get("views") or 0 # YouTube API returns string usually, handle safely
            if isinstance(views, str) and views.isdigit(): views = int(views)
            if views > 10000:
                s.credibility_score = min(70, s.credibility_score + 10)
                s.credibility_reason += " + Highly Viewed"
                
        elif rtype == "developer":
            stars = meta.get("stars") or 0
            if stars > 500:
                s.credibility_score = min(90, s.credibility_score + 20)
                s.credibility_reason += " + Popular Repo/Issue"

        updated_sources.append(s)

    msg = f"Scored credibility for {len(updated_sources)} sources."
    new_log = log_agent_action(state, "SourceCredibilityAgent", msg)
    
    return {
        "sources": updated_sources,
        "logs": [new_log]
    }
