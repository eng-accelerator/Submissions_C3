from langgraph.graph import StateGraph, END
from core.schema import ResearchState

from agents.planner import planner_node
from agents.retriever import retriever_node
from agents.credibility import credibility_node
from agents.analysis import analysis_node
from agents.contradictions import contradiction_node
from agents.insights import insights_node
from agents.report import report_node
from agents.stylist import stylist_node

from agents.community import community_signal_node
from agents.tutorial import tutorial_node
from agents.router import router_node
from agents.judge import judge_node, revise_node
from agents.debate import debate_round, moderator_node

# --- Routing Logic ---
def route_after_analysis(state: ResearchState):
    """Decide whether to run Community Agent."""
    groups = state.resource_groups or []
    if "Community" in groups or "News" in groups:
        return "community"
    return route_after_community(state) # Skip to next check

def route_after_community(state: ResearchState):
    """Decide whether to run Tutorial Agent."""
    groups = state.resource_groups or []
    if "Video" in groups or "Developer" in groups:
        return "tutorial"
    return route_after_tutorial(state) # Skip to next check

def route_after_tutorial(state: ResearchState):
    """Decide whether to run Contradictions Agent."""
    # Only run heavy contradiction analysis for Deep research or specific templates
    if state.depth == "Deep" or state.template == "Research Report" or state.research_objective == "Validate a Claim":
        return "contradictions"
    return "insights" # Skip to insights

def route_after_insights(state: ResearchState):
    """Branch based on Evaluation Mode."""
    mode = state.evaluation_mode
    if mode == "Debate":
        return "debater"
    return "report"

def route_after_report(state: ResearchState):
    """Branch for Judge Mode."""
    mode = state.evaluation_mode
    if mode == "Judge":
        return "judge"
    return "stylist"

def route_debate_loop(state: ResearchState):
    """Loop debate rounds."""
    transcript = state.debate_transcript or []
    # Default 2 rounds (4 turns)
    if len(transcript) < 4:
        return "debater"
    return "moderator"

def check_judge_feedback(state: ResearchState):
    """Route based on Judge's feedback."""
    if state.feedback:
        return "revise"
    return "stylist"

def build_graph():
    workflow = StateGraph(ResearchState)

    # Add Nodes
    workflow.add_node("router", router_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("credibility", credibility_node)
    workflow.add_node("analysis", analysis_node)
    
    workflow.add_node("community", community_signal_node)
    workflow.add_node("tutorial", tutorial_node)
    workflow.add_node("contradictions", contradiction_node)
    workflow.add_node("insights", insights_node)
    
    workflow.add_node("report", report_node)
    workflow.add_node("judge", judge_node)
    workflow.add_node("revise", revise_node)
    
    workflow.add_node("debater", debate_round)
    workflow.add_node("moderator", moderator_node)
    
    workflow.add_node("stylist", stylist_node)

    # Define Edges
    workflow.set_entry_point("router")
    workflow.add_edge("router", "planner")
    workflow.add_edge("planner", "retriever")
    workflow.add_edge("retriever", "credibility")
    workflow.add_edge("credibility", "analysis")
    
    # Conditional Chain: Analysis -> ... -> Insights
    workflow.add_conditional_edges(
        "analysis",
        route_after_analysis,
        {
            "community": "community", 
            "tutorial": "tutorial", 
            "contradictions": "contradictions", 
            "insights": "insights"
        }
    )

    workflow.add_conditional_edges(
        "community",
        route_after_community,
        {
            "tutorial": "tutorial", 
            "contradictions": "contradictions", 
            "insights": "insights"
        }
    )

    workflow.add_conditional_edges(
        "tutorial",
        route_after_tutorial,
        {
            "contradictions": "contradictions", 
            "insights": "insights"
        }
    )
    
    workflow.add_edge("contradictions", "insights")
    
    # Branching at Insights
    workflow.add_conditional_edges(
        "insights",
        route_after_insights,
        {
            "debater": "debater",
            "report": "report"
        }
    )
    
    # Debate Loop
    workflow.add_conditional_edges(
        "debater",
        route_debate_loop,
        {
            "debater": "debater",
            "moderator": "moderator"
        }
    )
    workflow.add_edge("moderator", "stylist")
    
    # Report -> (Judge or Stylist)
    workflow.add_conditional_edges(
        "report",
        route_after_report,
        {
            "judge": "judge",
            "stylist": "stylist"
        }
    )
    
    # Judge -> (Revise Loop or Stylist)
    workflow.add_conditional_edges(
        "judge",
        check_judge_feedback,
        {
            "revise": "revise",
            "stylist": "stylist"
        }
    )
    
    # Revise -> Judge (Verify fixes)
    workflow.add_edge("revise", "judge")
    
    workflow.add_edge("stylist", END)

    app = workflow.compile()
    return app
