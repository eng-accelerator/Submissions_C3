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
    
    # 1. RAG Check (Always include if present based on user request)
    from core.api_registry import APIRegistry
    from core.schema import Source
    
    current_sources = []
    rag_log = ""
    
    if state.context_data:
        # Create Source from Context
        pdf_source = Source(
            id="uploaded_doc",
            title="Uploaded Document (Context)",
            url="local://uploaded_file",
            snippet=state.context_data[:5000], # Keep a good chunk
            domain="Local",
            date="2024",
            credibility_score=100
        )
        current_sources.append(pdf_source)
        rag_log = f"Included uploaded document as primary source.\n"

    # 2. Retrieve (External) - ALWAYS execute as requested
    external_sources = retrieve_sources(
        state.question, 
        state.source_filters,
        state.resource_groups,
        state.source_types, 
        demo_mode=state.demo_mode
    )
    
    # Combine
    current_sources.extend(external_sources)
    
    # Logging
    top_sources = current_sources[:5]
    source_list = "\n".join([f"- [{s.title}]({s.url})" for s in top_sources])
    
    msg = f"{rag_log}Retrieved {len(external_sources)} external sources. Total: {len(current_sources)}.\nTop results:\n{source_list}"
    new_log = log_agent_action(state, "ContextualRetrieverAgent", msg)

    return {
        "sources": current_sources,
        "logs": [new_log]
    }
