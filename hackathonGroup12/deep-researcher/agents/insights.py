from agents.base import cached_call
from prompts import PROMPTS

def insights_node(state, llm):
    state["insights"] = cached_call(
        PROMPTS["insights"].format(
            analysis=state.get("analysis", ""),
            factchecked=state.get("factchecked", ""),
            critique=state.get("critique", "")
        ),
        llm,
        "Insights Agent"
    )
    return state
