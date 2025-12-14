from core.schema import ResearchState
from agents.base import log_agent_action
from tools.retrieval import retrieve_sources

def retriever_node(state: ResearchState):
    """
    ContextualRetrieverAgent:
    Executes the first step of the plan (or all steps) to find sources.
    For MVP/Hackathon, we probably just search the main question + first plan item.
    """
    # Simply using the first plan item or question to drive search
    query = state.question
    if state.plan:
        query = f"{state.question} {state.plan[0]}"
    
    # 2. Retrieve
    sources = retrieve_sources(
        state.question, 
        state.source_filters,
        state.resource_groups,
        state.source_types, 
        demo_mode=state.demo_mode
    )
    
    top_sources = sources[:5]
    source_list = "\n".join([f"- [{s.title}]({s.url})" for s in top_sources])
    
    msg = f"Retrieved {len(sources)} sources. Top results:\n{source_list}"
    new_log = log_agent_action(state, "ContextualRetrieverAgent", msg)

    return {
        "sources": sources,
        "logs": [new_log]
    }
