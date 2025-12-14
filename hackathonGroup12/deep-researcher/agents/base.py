import streamlit as st
from safe_invoke import safe_llm_invoke

@st.cache_data(show_spinner=False)
def cached_call(prompt: str, llm, agent: str):
    return safe_llm_invoke(llm, prompt, agent)
