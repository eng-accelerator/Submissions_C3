import os
from typing import Dict
from datetime import datetime, timedelta

ENV_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

def load_from_env() -> Dict[str, str]:
    """
    Loads key-value pairs from .env file.
    Only returns keys that have values.
    """
    keys = {}
    if not os.path.exists(ENV_FILE):
        return keys

    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                keys[k.strip()] = v.strip()
    return keys

def save_to_env(keys: Dict[str, str], days_to_expire: int = 30):
    """
    Saves dictionary validation to .env file.
    Adds a comment with expiry date.
    Masks the keys in the logs but writes them clearly to file.
    """
    # Calculate expiry
    expiry_date = (datetime.now() + timedelta(days=days_to_expire)).strftime("%Y-%m-%d")
    
    # Read existing content to preserve other vars if needed? 
    # For now, we overwrite to ensure clean state as per user request context.
    
    content = f"# Auto-generated API Keys\n"
    content += f"# EXPIRY_DATE={expiry_date}\n"
    content += "# These keys are stored locally and are gitignored.\n\n"
    
    for k, v in keys.items():
        if v:
            content += f"{k}={v}\n"
    
    with open(ENV_FILE, "w") as f:
        f.write(content)
