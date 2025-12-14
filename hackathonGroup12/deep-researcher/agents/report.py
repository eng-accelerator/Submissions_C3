from agents.base import cached_call
from prompts import PROMPTS

def report_node(state, llm):
    all_data = "\n".join([
        state.get(k, "") for k in
        ["retrieved","structured","analysis","factchecked","expert","critique","insights"]
    ])

    state["report"] = cached_call(
        PROMPTS["report"].format(all_data=all_data),
        llm,
        "Report Agent"
    )
    return state
