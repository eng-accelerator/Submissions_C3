from core.schema import ResearchState, Source
from core.api_registry import APIRegistry
from agents.base import log_agent_action
import time
# Retrieval imports
from tools.retrieval_perplexity import search_perplexity
from tools.retrieval_pubmed import search_pubmed
from tools.retrieval_clinicaltrials import search_clinical_trials
from tools.retrieval import retrieve_sources # Unified
import random

def router_node(state: ResearchState):
    """
    RouterAgent:
    Determines optimal tools and initial instructions based on Domain + Inputs.
    """
    domain = state.domain
    query = state.question
    
    # 1. Determine Sources based on Domain
    active_sources = []
    messages = []
    
    # Check for Perplexity capability (Native or OpenRouter)
    has_perplexity = APIRegistry.get_key("perplexity") or APIRegistry.get_key("openrouter_key")
    
    if domain == "Finance":
        if has_perplexity:
            messages.append("Using Perplexity (Native/OpenRouter) for real-time financial data.")
            active_sources.extend(search_perplexity(query))
        else:
            messages.append("Perplexity/OpenRouter Key missing. Falling back to Standard Web Search for Finance.")
            # Trigger Standard Web Search
            
    elif domain == "Medical":
        messages.append("Querying PubMed & ClinicalTrials.gov...")
        active_sources.extend(search_pubmed(query))
        active_sources.extend(search_clinical_trials(query))
        if has_perplexity:
             active_sources.extend(search_perplexity(f"Guidelines for {query}"))
             
    elif domain == "Academic":
        messages.append("Querying arXiv & OpenAlex...")
        # Reuse existing robust academic search
        state.resource_groups = ["Academic"]
        state.source_types = ["arXiv", "OpenAlex"]
        # Standard retrieval will pick this up in the next step (RetrieverNode)
        # OR we can pre-fetch here.
        # Let's let RetrieverNode handle standard groups, but for domain specific tools we fetch here.
        
    elif domain == "Product/Tool Comparison":
        active_tools = []
        # Check keys
        if APIRegistry.get_key("reddit_client_id"): active_tools.append("Reddit")
        if APIRegistry.get_key("youtube_api_key"): active_tools.append("YouTube")
        if APIRegistry.get_key("github_token"): active_tools.append("GitHub")
        active_tools.append("Hacker News") # Public
        
        messages.append(f"Querying Community Signals ({', '.join(active_tools)})...")
        # Set standardized groups for Retriever
        state.resource_groups = ["Community", "Video", "Developer"]
        state.source_types = active_tools
        
    elif domain == "Quick Content Research":
        messages.append("Gathering viral hooks & sentiment...")
        state.resource_groups = ["Community", "Web"]
        state.source_types = ["Reddit", "Web"]
        
    else: # General
        state.resource_groups = ["Web"]
        state.source_types = ["Web"]
        
    # Pre-populate discovered sources from specialized tools
    current_sources = state.sources or []
    current_sources.extend(active_sources)
    
    # Update State
    new_log = log_agent_action(state, "ResearchRouter", " | ".join(messages))
    
    return {
        "sources": current_sources,
        "resource_groups": state.resource_groups,
        "source_types": state.source_types,
        "logs": [new_log]
    }
