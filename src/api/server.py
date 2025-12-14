from dotenv import load_dotenv

# Load environment variables from .env file before importing agents
load_dotenv()

from src.agents.adaptive_repair_agent import AdaptiveRepairAgent
from src.agents.error_diagnosis_agent import ErrorDiagnosisAgent
from src.agents.execution_agent import ExecutionAgent
from src.agents.script_generator_agent import ScriptGeneratorAgent
from src.agents.flow_discovery_agent import FlowDiscoveryAgent
from src.agents.workflow_graph import graph
from fastapi import FastAPI
from pydantic import BaseModel
import traceback


app = FastAPI()


flow_agent = FlowDiscoveryAgent()
script_agent = ScriptGeneratorAgent()
exec_agent = ExecutionAgent()
diagnosis_agent = ErrorDiagnosisAgent()
repair_agent = AdaptiveRepairAgent()


class URLInput(BaseModel):
    url: str


class FlowInput(BaseModel):
    flow: str


class ExecInput(BaseModel):
    script: str


class DiagnosisInput(BaseModel):
    stderr: str
    script: str


@app.post("/discover-flow")
def discover_flow(data: URLInput):
    return flow_agent.discover(data.url)


@app.post("/generate-script")
def generate_script(data: FlowInput):
    return script_agent.generate_script(data.flow)


@app.post("/execute-script")
def execute_script(data: ExecInput):
    return exec_agent.execute(data.script)


@app.post("/diagnose")
def diagnose(data: DiagnosisInput):
    diagnosis = diagnosis_agent.diagnose(data.stderr)
    return {"diagnosis": diagnosis}


@app.post("/repair")
def repair(data: DiagnosisInput):
    diagnosis = diagnosis_agent.diagnose(data.stderr)
    return repair_agent.repair(data.script, diagnosis)


@app.post("/run-automation")
def run_automation(data: URLInput):
    initial_state = {"url": data.url, "error_count": 0, "max_retries": 3}
    try:
        final_state = graph.invoke(initial_state, config={"recursion_limit": 100})
        return final_state
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}
