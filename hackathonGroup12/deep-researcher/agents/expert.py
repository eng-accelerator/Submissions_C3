from agents.base import cached_call
from prompts import PROMPTS

def expert_node(state, llm):
    state["expert"] = cached_call(
        PROMPTS["expert"].format(
            factchecked=state.get("factchecked", "")
        ),
        llm,
        "Expert Agent"
    )
    return state
