from agents.base import cached_call
from prompts import PROMPTS

def structurer_node(state, llm):
    state["structured"] = cached_call(
        PROMPTS["structurer"].format(
            retrieved=state.get("retrieved", "")
        ),
        llm,
        "Structurer Agent"
    )
    return state
