import time
from core.schema import ResearchState, AgentLog

def log_agent_action(state: ResearchState, agent_name: str, message: str):
    """
    Appends a log entry to the state.
    Note: In LangGraph, we typically return the update.
    This helper is for side-effect free logging if we were passing mutable state,
    but for LangGraph reducers, we should return {'logs': [new_log]}.
    """
    return AgentLog(
        agent_name=agent_name,
        message=message,
        timestamp=time.time()
    )
