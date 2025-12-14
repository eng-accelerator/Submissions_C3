from langgraph.graph import StateGraph, START, END
from typing import Optional, List, Dict, Any, TypedDict
from src.agents.flow_discovery_agent import FlowDiscoveryAgent
from src.agents.script_generator_agent import ScriptGeneratorAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.error_diagnosis_agent import ErrorDiagnosisAgent
from src.agents.adaptive_repair_agent import AdaptiveRepairAgent
from src.agents.regression_monitor_agent import RegressionMonitorAgent


class WorkflowState(TypedDict, total=False):
    url: str
    flows: Optional[List[Dict[str, Any]]]
    selected_flow: Optional[Dict[str, Any]]
    script: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    diagnosis: Optional[str]
    repaired_script: Optional[str]
    regression_result: Optional[Dict[str, Any]]
    error_count: int
    max_retries: int


# Initialize agents
flow_agent = FlowDiscoveryAgent()
script_agent = ScriptGeneratorAgent()
exec_agent = ExecutionAgent()
diagnosis_agent = ErrorDiagnosisAgent()
repair_agent = AdaptiveRepairAgent()
regression_agent = RegressionMonitorAgent()


def discover_flow_node(state: Dict[str, Any]) -> Dict[str, Any]:
    result = flow_agent.discover(state["url"])
    updates = {}
    if "flows" in result:
        updates["flows"] = result["flows"]
        if result["flows"]:
            updates["selected_flow"] = result["flows"][0]
    return updates


def generate_script_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("selected_flow"):
        flow_description = f"Name: {state['selected_flow']['name']}\nDescription: {state['selected_flow']['description']}\nSteps: {', '.join(state['selected_flow']['steps'])}"
        return {"script": script_agent.generate_script(flow_description)}
    return {}


def execute_script_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("script"):
        return {"execution_result": exec_agent.execute(state["script"])}
    return {}


def handle_error_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("execution_result") and state["execution_result"].get("stderr"):
        return {"error_count": state.get("error_count", 0) + 1}
    return {}


def diagnose_error_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("execution_result") and state["execution_result"].get("stderr"):
        return {"diagnosis": diagnosis_agent.diagnose(state["execution_result"]["stderr"])}
    return {}


def repair_script_node(state: Dict[str, Any]) -> Dict[str, Any]:
    if state.get("diagnosis") and state.get("script"):
        repaired = repair_agent.repair(state["script"], state["diagnosis"])
        return {"repaired_script": repaired, "script": repaired}
    return {}


def compare_regression_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # Placeholder
    return {}


def should_retry(state: Dict[str, Any]) -> str:
    if state.get("error_count", 0) < state.get("max_retries", 3):
        return "repair"
    return "success"


# Build the graph
workflow = StateGraph(WorkflowState)

workflow.add_node("discover", discover_flow_node)
workflow.add_node("generate", generate_script_node)
workflow.add_node("execute", execute_script_node)
workflow.add_node("handle_error", handle_error_node)
workflow.add_node("diagnose", diagnose_error_node)
workflow.add_node("repair", repair_script_node)
workflow.add_node("compare", compare_regression_node)

workflow.add_edge(START, "discover")
workflow.add_edge("discover", "generate")
workflow.add_edge("generate", "execute")
workflow.add_edge("execute", "handle_error")
workflow.add_conditional_edges(
    "handle_error",
    should_retry,
    {
        "repair": "diagnose",
        "success": "compare"
    }
)
workflow.add_edge("diagnose", "repair")
workflow.add_edge("repair", "execute")
workflow.add_edge("compare", END)

# Compile the graph
graph = workflow.compile()