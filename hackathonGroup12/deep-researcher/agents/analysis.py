from agents.base import cached_call
from prompts import PROMPTS
from logger import logger

def analysis_node(state, llm):
    try:
        state["analysis"] = cached_call(
            PROMPTS["analysis"].format(
                structured=state.get("structured", "")
            ),
            llm,
            "Analysis Agent"
        )
    except Exception as e:
        logger.error(e)
        state["analysis"] = "❌ Analysis failed."
    return state
