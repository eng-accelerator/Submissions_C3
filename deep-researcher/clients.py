from langchain_openai import ChatOpenAI
import streamlit as st
from tavily import TavilyClient

@st.cache_resource(show_spinner=False)
def init_llm(openrouter_key: str):
    """Initialize OpenRouter LLM."""
    return ChatOpenAI(
        model="openai/gpt-4o",
        temperature=0.1,
        api_key=openrouter_key,
        openai_api_base="https://openrouter.ai/api/v1"
    )

@st.cache_resource(show_spinner=False)
def init_tavily(tavily_api_key: str):
    """Initialize Tavily client."""
    return TavilyClient(api_key=tavily_api_key)
