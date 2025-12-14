import streamlit as st
from logger import logger
from errors import LLMInvocationError

def safe_llm_invoke(llm, prompt: str, agent: str) -> str:
    try:
        return llm.invoke(prompt).content
    except Exception as e:
        logger.exception(f"{agent} failed")
        st.warning(f"⚠️ {agent} encountered an error.")
        raise LLMInvocationError(str(e))
