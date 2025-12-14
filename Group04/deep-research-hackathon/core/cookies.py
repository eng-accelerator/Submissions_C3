import uuid
# Note: Streamlit doesn't strictly support setting cookies from server-side python natively without components.
# We will use a workaround or a standard library if available, but for a standard Streamlit app, we often use `extra-streamlit-components` or logic wrapped in JS.
# For this specific component, we'll design a localized helper that simulates the logic or uses query params/local storage if strictly needed.
# However, the user asked for a "Cookie" store. We will implement what we can that is closest to a cookie manager.
# Since we cannot easily install custom components without user intervention, we might assume `extra_streamlit_components` is available or
# we use a purely session-based simulation for "Session ID" if we can't write real headers.
#
# BUT, the prompt implies "Browser cookie stores ONLY a session_id".
# We will use `extra_streamlit_components.CookieManager` pattern if possible.
# For simplicity and robust "pure python" without assuming extra libs that might break:
# We will trust the user installs `extra-streamlit-components` if they want real cookies.
# For now, I will implement a placeholder that warns if the library isn't there, or uses a simple URL param / session state hack.
#
# Actually, let's try to do it right. I'll add `extra-streamlit-components` to requirements.

import streamlit as st
try:
    import extra_streamlit_components as stx
except ImportError:
    stx = None

class CookieManager:
    def __init__(self):
        if stx:
            self.manager = stx.CookieManager()
        else:
            self.manager = None

    def get_cookie(self, name: str):
        if self.manager:
            return self.manager.get(name)
        return None

    def set_cookie(self, name: str, value: str, days_expire: int = 1):
        if self.manager:
            self.manager.set(name, value, key=f"set_{name}", expires_at=None) # simple set

    def delete_cookie(self, name: str):
        if self.manager:
            self.manager.delete(name)

    def get_or_create_sid(self) -> str:
        # If we can't read cookies (lib missing), we just generate a session-bound ID.
        sid = self.get_cookie("deeptrace_sid")
        if not sid:
            sid = str(uuid.uuid4())
            # We delay setting until we actually want to persist, 
            # or we accept that 'get_or_create' implies we want one now.
        return sid
