from agents.base import cached_call
from prompts import PROMPTS

def factcheck_node(state, llm):
    state["factchecked"] = cached_call(
        PROMPTS["factcheck"].format(
            analysis=state.get("analysis", "")
        ),
        llm,
        "Factcheck Agent"
    )
    return state
