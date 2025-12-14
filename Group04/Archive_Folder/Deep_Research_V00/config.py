import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration class to manage API keys and settings.
    Prioritizes Streamlit secrets/sidebar inputs over environment variables.
    """
    
    @staticmethod
    def get_api_key(service_name: str) -> str:
        """
        Retrieve API key for a given service (e.g., 'openai', 'tavily').
        """
        # 1. Try Streamlit Session State (User Input) - only if streamlit is initialized
        try:
            key_name = f"{service_name}_api_key"
            if hasattr(st, 'session_state') and key_name in st.session_state and st.session_state[key_name]:
                return st.session_state[key_name]
        except (RuntimeError, AttributeError):
            # Streamlit not initialized or not in streamlit context
            pass
        
        # 2. Try Environment Variable
        env_key = os.getenv(f"{service_name.upper()}_API_KEY")
        if env_key:
            return env_key
            
        return None

    @staticmethod
    def validate_keys():
        """
        Check which keys are available and return a status dict.
        """
        try:
            return {
                "openai": bool(Config.get_api_key("openai")),
                "anthropic": bool(Config.get_api_key("anthropic")),
                "gemini": bool(Config.get_api_key("gemini")),
                "tavily": bool(Config.get_api_key("tavily")),
                "serper": bool(Config.get_api_key("serper")),
            }
        except Exception:
            # Fallback if streamlit context issues
            return {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "gemini": bool(os.getenv("GEMINI_API_KEY")),
                "tavily": bool(os.getenv("TAVILY_API_KEY")),
                "serper": bool(os.getenv("SERPER_API_KEY")),
            }
