from agents.base import cached_call
from prompts import PROMPTS

def critique_node(state, llm):
    state["critique"] = cached_call(
        PROMPTS["redteam"].format(
            expert=state.get("expert", "")
        ),
        llm,
        "Red Team Agent"
    )
    return state
