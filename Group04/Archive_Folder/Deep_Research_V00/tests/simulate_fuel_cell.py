import sys
import os
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock Config to avoid key errors
with patch('config.Config.get_api_key', return_value="dummy_key"):
    from graph.workflow import app_graph
    from agents.planner import ResearchPlan, ResearchScope, SubQuery
    from agents.reflection import ReflectionValidation

def mock_llm_invoke(*args, **kwargs):
    # Determine which agent is calling based on prompt content (simplified)
    # real implementation would inspect the prompt structure
    input_data = args[0] if args else kwargs
    prompt_str = str(input_data)
    
    if "Lead Research Planner" in prompt_str:
        return ResearchPlan(
            main_objective="Investigate latest developments in Fuel Cell technology.",
            scope_and_assumptions=ResearchScope(
                scope="Global technological advancements.",
                assumptions=["Focus on PEM and SOFC types."],
                limitations=["Publicly available academic data only."],
                time_horizon="Last 2 years"
            ),
            sub_queries=[
                SubQuery(query="latest PEM fuel cell efficiency records 2024", source_type="academic", rationale="Check efficiency gains."),
                SubQuery(query="Solid Oxide Fuel Cell durability improvements", source_type="technical", rationale="Check lifespan.")
            ],
            required_information=["Efficiency metrics", "Cost reduction data"]
        )
    elif "Critical Research Analyst" in prompt_str:
        return {
            "summary": "Recent findings suggest a 15% increase in PEM density.",
            "key_findings": ["New catalyst reduces platinum usage.", "Toyota announced new Mirai stack."],
            "contradictions": [],
            "uncertainties": ["Long-term stability of new catalyst."],
            "sources_used": [1]
        }
    elif "Visionary Thinker" in prompt_str:
        return ["Fuel cells are becoming viable for heavy trucking.", "Green hydrogen costs are the main bottleneck, not the cells themselves."]
    elif "Research Manager" in prompt_str:
        return ReflectionValidation(
            is_sufficient=True, 
            missing_information=[], 
            follow_up_queries=[]
        )
    elif "Score" in prompt_str or "Fact Checker" in prompt_str:
        return [{"source": "Nature Energy", "score": 95, "reason": "Top journal"}, {"source": "TechCrunch", "score": 85, "reason": "Reliable tech news"}]
    elif "Professional Research Writer" in prompt_str:
        return """# Research Report: Fuel Cell Developments
        
## Executive Summary
Recent breakthroughs in 2024 have focused on reducing platinum group metals (PGM) in PEM fuel cells, significantly lowering costs.

## Key Findings
- **PEM Efficiency**: 15% increase in power density reported by top labs.
- **Durability**: Solid Oxide Fuel Cells (SOFC) have reached 100,000 hour milestones in stationary tests.

## Insights
The shift is moving from passenger vehicles to heavy-duty logistics and maritime applications.
        """
    return "Mock LLM Response"

def mock_search(*args, **kwargs):
    query = args[0] if args else ""
    return [
        {"url": "https://nature.com/articles/s41560-024", "content": "New catalyst design improves PEM fuel cell performance by 15%..."},
        {"url": "https://energy.gov/h2", "content": "DOE sets new targets for heavy duty truck fuel cells..."}
    ]

def run_simulation():
    print(">>> Starting Fuel Cell Research Simulation...")
    
    # Patch LLM and Search
    with patch('modules.llm_factory.LLMFactory.create_llm') as MockFactory:
        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = mock_llm_invoke
        MockFactory.return_value = mock_llm
        
        with patch('tools.search_tools.SearchTools.search', side_effect=mock_search):
            
            # Re-import to apply patches if necessary, but here we perform dependency injection via patching the instances creation in the agents
            # Since agents are instantiated at module level in workflow.py, we might need to recreate them or patch the instances directly
            # Easier approach: Patch the classes used inside the agents
            
            from graph.workflow import app_graph
            
            # We need to manually inject mocks because graph initialized agents already
            import graph.workflow
            graph.workflow.planner.llm = mock_llm
            graph.workflow.retriever.llm = mock_llm
            graph.workflow.retriever.search_tool.search = mock_search
            graph.workflow.analyst.llm = mock_llm
            graph.workflow.insight.llm = mock_llm
            graph.workflow.reflector.llm = mock_llm
            graph.workflow.credibility.llm = mock_llm
            graph.workflow.reporter.llm = mock_llm

            initial_state = {
                "task": "latest development in fuel cell",
                "discipline": "Scientific & Academic Research",
                "uploaded_files": [],
                "iteration_count": 0,
                "findings": []
            }
            
            print(">>> Invoking Orchestrator...")
            final_state = app_graph.invoke(initial_state)
            
            print("\n" + "="*50)
            print("SIMULATION RESULT")
            print("="*50)
            print(final_state.get("final_report"))
            print("="*50)

if __name__ == "__main__":
    run_simulation()
