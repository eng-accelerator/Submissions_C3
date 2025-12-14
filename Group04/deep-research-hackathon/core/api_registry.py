from typing import Dict, Optional
import streamlit as st

class APIRegistry:
    """
    In-memory registry for API keys.
    Wraps st.session_state to ensure keys are never written to disk/logs
    except via the explicit SecureStore.
    """
    
    SESSION_KEY = "DEEPTRACE_API_KEYS"

    @staticmethod
    def _get_store() -> Dict[str, str]:
        if APIRegistry.SESSION_KEY not in st.session_state:
            st.session_state[APIRegistry.SESSION_KEY] = {}
        return st.session_state[APIRegistry.SESSION_KEY]

    @staticmethod
    def register_key(provider: str, key: str):
        """Register a key for the current session."""
        store = APIRegistry._get_store()
        if key and key.strip():
            store[provider.lower()] = key.strip()

    @staticmethod
    def get_key(provider: str) -> Optional[str]:
        """Retrieve a key. Returns None if missing."""
        store = APIRegistry._get_store()
        return store.get(provider.lower())

    @staticmethod
    def has_key(provider: str) -> bool:
        return APIRegistry.get_key(provider) is not None

    @staticmethod
    def clear_all():
        if APIRegistry.SESSION_KEY in st.session_state:
             st.session_state[APIRegistry.SESSION_KEY] = {}
