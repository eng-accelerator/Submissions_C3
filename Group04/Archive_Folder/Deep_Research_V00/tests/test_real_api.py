import sys
import os
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Force reload environment
load_dotenv(override=True)

from modules.llm_factory import LLMFactory
from tools.search_tools import SearchTools

def test_live_connections():
    print(">>> Testing Live API Connections...")
    
    # 1. Test Search (Tavily)
    print("\n1. Testing Tavily Search...")
    try:
        search = SearchTools.get_search_tool()
        results = search.invoke("current CEO of OpenAI")
        print(f"   Search Results Found: {len(results) > 0}")
        print(f"   Sample: {str(results)[:100]}...")
    except Exception as e:
        print(f"   [!] Tavily Search Failed: {e}")

    # 2. Test LLM (OpenRouter/OpenAI)
    print("\n2. Testing LLM Generation...")
    try:
        llm = LLMFactory.create_llm("openai")
        if llm:
            response = llm.invoke("Hello, are you working?")
            print(f"   LLM Response: {response.content}")
        else:
            print("   [!] LLM Integration returned None")
    except Exception as e:
        print(f"   [!] LLM Failed: {e}")

if __name__ == "__main__":
    test_live_connections()
