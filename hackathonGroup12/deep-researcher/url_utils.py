import re

def remove_urls(text: str) -> str:
    return re.sub(r'https?://\S+|www\.\S+', '', text)
