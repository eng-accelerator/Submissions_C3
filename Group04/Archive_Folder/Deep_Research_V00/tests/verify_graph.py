import sys
import os

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



def test_backend():
    print("Testing Backend Imports...")
    try:
        print("Importing config...")
        import config
        print("Importing logging...")
        import utils.logging
        print("Importing LLMFactory...")
        from modules.llm_factory import LLMFactory
        print("Importing Planner...")
        from agents.planner import PlannerAgent
        print("Importing Retriever...")
        from agents.retriever import RetrieverAgent
        print("Importing Analyst...")
        from agents.analyst import AnalystAgent
        print("Importing Insight...")
        from agents.insight import InsightAgent
        print("Importing Reflection...")
        from agents.reflection import ReflectionAgent
        print("Importing State...")
        from graph.state import AgentState
        print("Importing Graph...")
        from graph.workflow import app_graph
        print("Imports Successful!")
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_backend()
