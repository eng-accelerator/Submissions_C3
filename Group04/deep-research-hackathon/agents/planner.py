from core.schema import ResearchState
from agents.base import log_agent_action
from core.api_registry import APIRegistry

def planner_node(state: ResearchState):
    """
    ResearchPlannerAgent:
    Decomposes the main question into a step-by-step research plan.
    """
    question = state.question
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    
    if not llm_key:
        msg = "Planning skipped: Missing LLM Key."
        return {"plan": [], "logs": [log_agent_action(state, "ResearchPlannerAgent", msg)]}

    from core.llm import get_llm
    from langchain_core.messages import SystemMessage, HumanMessage
    
    try:
        llm = get_llm()
        if llm:
            # Objective-based strategies
            obj = state.research_objective
            strategy_prompt = ""
            
            if obj == "Learn":
                strategy_prompt = "Focus on foundational concepts, history, and key definitions."
            elif obj == "Compare":
                strategy_prompt = "Create steps to compare distinct entities, pros/cons, and feature tables."
            elif obj == "Decide":
                strategy_prompt = "Focus on decision criteria, weighting factors, and final recommendation logic."
            elif obj == "Forecast":
                strategy_prompt = "Focus on trends, future predictions, and growth factors."
            elif obj == "Validate a Claim":
                strategy_prompt = f"Focus on fact-checking this specific claim: '{state.claim_to_validate or state.question}'."

            prompt = (f"Decompose this research question into 3 distinct sub-questions or search queries: '{question}'.\n"
          f"Domain: {state.domain}\n"
          f"Additional Context (Use this if relevant): {state.context_data}\n"
          f"Objective: {obj}. Strategy: {strategy_prompt}\n"
          "Return ONLY a python list of strings.")
            response = llm.invoke([SystemMessage(content="You are a research planner."), HumanMessage(content=prompt)])
            # Naive parsing
            import ast
            # Clean markdown code blocks if any
            content = response.content.replace("```python", "").replace("```", "").strip()
            try:
                plan = ast.literal_eval(content)
                if not isinstance(plan, list): raise ValueError
                
                plan_list = "\n".join([f"- {step}" for step in plan])
                msg = f"Generated plan:\n{plan_list}"
            except:
                plan = [f"{question} overview", f"{question} statistics", f"{question} challenges"]
                msg = "LLM Parse Error, using basic fallback plan (non-demo)."
        else:
             msg = "LLM Initialization failed."
             plan = []
    except Exception as e:
        msg = f"LLM Error: {e}"
        plan = []

    new_log = log_agent_action(state, "ResearchPlannerAgent", msg)
    
    return {
        "plan": plan,
        "logs": [new_log]
    }
