import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# TechCrunch Settings
TECHCRUNCH_URL = "https://techcrunch.com"
SEARCH_KEYWORD = "AI"

# Browser Settings
HEADLESS_MODE = False  # Set to False to see the browser in action
BROWSER_TIMEOUT = 30000  # ms

# Output Settings
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)
