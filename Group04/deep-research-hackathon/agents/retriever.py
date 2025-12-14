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
    
    # 1. RAG Check (PDF First)
    from core.api_registry import APIRegistry
    from core.schema import Source
    
    llm_key = APIRegistry.get_key("llm") or APIRegistry.get_key("openrouter_key") or APIRegistry.get_key("anthropic_key")
    context_source = None
    
    if state.context_data and llm_key:
        try:
            from core.llm import get_llm
            from langchain_core.messages import SystemMessage, HumanMessage
            import json
            
            llm = get_llm()
            # Strict check: Does the context answer the MAIN question?
            check_prompt = f"""
            Analyze the following context in relation to the query: '{state.question}'.
            Context: {state.context_data[:5000]}...
            
            Does this context contain sufficient information to comprehensively answer the query?
            Return JSON: {{"sufficient": boolean, "reason": "why"}}
            """
            res = llm.invoke([SystemMessage(content="You are a dataset evaluator."), HumanMessage(content=check_prompt)])
            clean = res.content.replace("```json", "").replace("```", "").strip()
            evaluation = json.loads(clean)
            
            if evaluation.get("sufficient", False):
                msg = f"Found sufficient answer in uploaded document. Reason: {evaluation.get('reason')}. Skipping Web Search."
                pdf_source = Source(
                    id="uploaded_doc",
                    title="Uploaded Document (Context)",
                    url="local://uploaded_file",
                    snippet=state.context_data[:2000],
                    domain="Local",
                    date="2024",
                    credibility_score=100
                )
                return {
                    "sources": [pdf_source],
                    "logs": [log_agent_action(state, "ContextualRetrieverAgent", msg)]
                }
            else:
                # Append context as a source but continue to search
                msg_ctx = f"Context checked but found insufficient ({evaluation.get('reason')}). Proceeding with API Search."
                # We can add this log but continue execution
                
        except Exception as e:
            # Continue to web search if check fails
            print(f"RAG Check Error: {e}")

    # 2. Retrieve (External)
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
