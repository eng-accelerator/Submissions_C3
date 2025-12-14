from core.schema import ResearchState, AgentLog
from agents.base import log_agent_action
from core.api_registry import APIRegistry

def tutorial_node(state: ResearchState):
    """
    TutorialHowToAgent:
    Analyzes YouTube/GitHub sources to extract practical steps, code snippets, and gotchas.
    """
    # 1. Filter for video/dev sources
    tut_sources = [s for s in state.sources if s.domain in ["youtube.com", "github.com"] or s.metadata.get("resource_type") in ["video", "developer"]]
    
    if not tut_sources:
        return {"practical_steps": [], "logs": [log_agent_action(state, "TutorialHowToAgent", "No tutorial sources found.")]}

    # 2. LLM Analysis
    steps = []
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    msg = "No steps extracted."
    
    if not llm_key:
         msg = "Tutorial analysis skipped: Missing LLM Key."
         steps = []
    else:
        from core.llm import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        
        try:
            llm = get_llm()
            snippet_text = "\n\n".join([f"Source: {s.title} ({s.domain})\nContent: {s.snippet}" for s in tut_sources[:15]])
            
            prompt = (f"Analyze these tutorial/developer resources regarding '{state.question}'.\n"
                      f"Extract a 'Practical Playbook' or 'How-To' guide which includes:\n"
                      f"- Step-by-step instructions\n"
                      f"- Common pitfalls (gotchas)\n"
                      f"- Key configuration or code insights\n"
                      f"Format as a Python list of strings. Do not use markdown.\n\n"
                      f"Sources:\n{snippet_text}")

            response = llm.invoke([
                SystemMessage(content="You are a technical instructor and developer advocate."),
                HumanMessage(content=prompt)
            ])
            
            # Naive parse
            content = response.content.replace("```python", "").replace("```", "").strip()
            if content.startswith("[") and content.endswith("]"):
                import ast
                steps = ast.literal_eval(content)
            else:
                steps = [line.strip("- *") for line in content.split("\n") if line.strip()]

            msg = f"Extracted {len(steps)} practical steps."

        except Exception as e:
            msg = f"LLM Error: {e}"
            steps = []

    return {
        "practical_steps": steps,
        "logs": [log_agent_action(state, "TutorialHowToAgent", msg)]
    }
