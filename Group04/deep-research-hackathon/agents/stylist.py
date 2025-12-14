from core.schema import ResearchState
from agents.base import log_agent_action

def stylist_node(state: ResearchState):
    """
    TemplateStylistAgent:
    Adapts the report_md into the requested format (LinkedIn, Newsletter, etc).
    """
    template = state.template
    original = state.report_md
    
    stylized = ""
    
    if template == "LinkedIn Post":
        stylized = "🚀 **New Research Findings**\n\n"
        stylized += f"I just researched '{state.question}' and here's what I found:\n\n"
        for i in state.insights:
            stylized += f"✅ {i}\n"
        stylized += "\n#AI #Research #TechTrends"
        
    elif template == "Marketing Brief":
        stylized = f"**INTERNAL MARKETING BRIEF**: {state.question}\n\n"
        stylized += "**Key Selling Points**:\n"
        for c in state.claims:
            if c.status == "Verified":
                stylized += f"- {c.text}\n"
    else:
        # Default / Research Report
        stylized = original

    msg = f"Applied template: {template}"
    new_log = log_agent_action(state, "TemplateStylistAgent", msg)

    return {
        "templated_output": stylized,
        "logs": [new_log]
    }
