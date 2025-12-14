from core.schema import ResearchState, AgentLog
from agents.base import log_agent_action
from core.api_registry import APIRegistry

def community_signal_node(state: ResearchState):
    """
    CommunitySignalAgent:
    Analyzes Reddit/HN sources to extract pain points, sentiment, and disagreements.
    """
    # 1. Filter for community sources
    comm_sources = [s for s in state.sources if s.domain in ["reddit.com", "news.ycombinator.com"] or s.metadata.get("resource_type") == "community"]
    
    if not comm_sources:
        return {"community_signals": [], "logs": [log_agent_action(state, "CommunitySignalAgent", "No community sources found to analyze.")]}

    # 2. LLM Analysis
    signals = []
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    is_demo = not llm_key
    msg = "No signals extracted."
    
    if not is_demo:
        from core.llm import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        
        try:
            llm = get_llm()
            # If no LLM available, log error
            if not llm:
                 return {"community_signals": [], "logs": [log_agent_action(state, "CommunitySignalAgent", "Analyst skipped: No LLM Key.")]}

            snippet_text = "\n\n".join([f"Source: {s.title} ({s.domain})\nContent: {s.snippet}" for s in comm_sources[:15]])
            
            prompt = (f"Analyze these community discussions regarding '{state.question}'.\n"
                      f"Identify 3-5 distinct 'signals' such as:\n"
                      f"- Recurring pain points\n"
                      f"- Highly recommended tools/solutions\n"
                      f"- Major controversies or disagreements\n"
                      f"Format as a Python list of strings. Do not use markdown.\n\n"
                      f"Sources:\n{snippet_text}")

            response = llm.invoke([
                SystemMessage(content="You are an expert at analyzing online community sentiment and discussions."),
                HumanMessage(content=prompt)
            ])
            
            # Naive parse
            content = response.content.replace("```python", "").replace("```", "").strip()
            # If list format, parse, else split lines
            if content.startswith("[") and content.endswith("]"):
                import ast
                signals = ast.literal_eval(content)
            else:
                signals = [line.strip("- *") for line in content.split("\n") if line.strip()]

            msg = f"Extracted {len(signals)} community signals."

        except Exception as e:
            msg = f"LLM Info Extraction Failed: {e}"
            signals = []
    else:
        msg = "Community analysis skipped (No LLM Key)."
        signals = []

    return {
        "community_signals": signals,
        "logs": [log_agent_action(state, "CommunitySignalAgent", msg)]
    }
