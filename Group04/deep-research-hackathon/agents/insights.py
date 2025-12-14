from core.schema import ResearchState
from agents.base import log_agent_action

def insights_node(state: ResearchState):
    """
    InsightGenerationAgent:
    Synthesize high-level trends or 'between the lines' insights.
    """
    insights = [
        "Rapid adoption of agentic workflows is outacing security protocols.",
        "There is a growing divide between academic skepticism and industry hype regarding autonomous capabilities."
    ]
    
    msg = "Generated 2 key insights."
    new_log = log_agent_action(state, "InsightGenerationAgent", msg)

    return {
        "insights": insights,
        "logs": [new_log]
    }
