# components/orchestration.py

"""
Component 5: Agent Orchestration System
Technology: LangGraph
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
from datetime import datetime
import json


class AnalysisState(TypedDict):
    """
    Function 5.1: Define analysis state schema
    """
    # Inputs
    image_base64: str
    image_embedding: list
    platform: str
    creative_type: str
    enabled_agents: list
    image_metadata: dict
    model_used: str
    top_k: int
    
    # Agent outputs
    visual_analysis: dict
    ux_analysis: dict
    market_analysis: dict
    conversion_analysis: dict
    brand_analysis: dict
    
    # Final output
    final_report: dict
    error: str
    
    # Progress tracking
    current_step: int
    total_steps: int
    step_message: str


def aggregate_results_node(state):
    """
    Function 5.4: Aggregate all agent outputs into final report
    
    Args:
        state: Current analysis state
    
    Returns:
        dict: Updated state with final_report
    """
    print("📊 Aggregating results...")
    
    def safe_score(value):
        """Convert value to float if possible, else return 0."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
    visual = state.get('visual_analysis', {})
    ux = state.get('ux_analysis', {})
    market = state.get('market_analysis', {})
    conversion = state.get('conversion_analysis', {})
    brand = state.get('brand_analysis', {})
    agent_errors = {}
    def _coerce_payload(name, payload):
        # If payload is not a dict or missing expected keys, flag it.
        if not isinstance(payload, dict):
            agent_errors[name] = "Invalid agent payload (non-dict)"
            return {"error": "Invalid agent payload"}
        if "error" in payload:
            agent_errors[name] = payload.get("error")
        return payload

    visual = _coerce_payload("visual", visual)
    ux = _coerce_payload("ux", ux)
    market = _coerce_payload("market", market)
    conversion = _coerce_payload("conversion", conversion)
    brand = _coerce_payload("brand", brand)
    
    # Calculate overall score (weighted average)
    visual_score = safe_score(visual.get('overall_score', 0))
    ux_score = safe_score(ux.get('overall_score', 0))
    market_score = safe_score(market.get('overall_score', 0))
    conversion_score = safe_score(conversion.get('overall_score', 0))
    brand_score = safe_score(brand.get('overall_score', 0))
    
    overall_score = (
        visual_score * 0.2 +
        ux_score * 0.2 +
        market_score * 0.2 +
        conversion_score * 0.2 +
        brand_score * 0.2
    )
    
    # Aggregate all recommendations
    all_recommendations = []
    
    # From visual analysis
    if 'color_analysis' in visual:
        print("📊 Aggregating results color_analysis ...")
        recs = visual['color_analysis'].get('recommendations', [])
        for rec in recs[:3]:  # Top 3
            all_recommendations.append({
                "source": "Visual - Color",
                "priority": "high",
                "recommendation": rec
            })
    
    if 'layout_analysis' in visual:
        print("📊 Aggregating results layout_analysis ...")
        recs = visual['layout_analysis'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Visual - Layout",
                "priority": "medium",
                "recommendation": rec
            })
    
    if 'typography' in visual:
        print("📊 Aggregating results typography ...")
        recs = visual['typography'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Visual - Typography",
                "priority": "medium",
                "recommendation": rec
            })
    
    # From UX analysis
    if 'usability' in ux:
        print("📊 Aggregating results usability ...")
        recs = ux['usability'].get('recommendations', [])
        for rec in recs[:3]:
            all_recommendations.append({
                "source": "UX - Usability",
                "priority": "high",
                "recommendation": rec
            })
    
    if 'accessibility' in ux:
        print("📊 Aggregating results accessibility ...")
        recs = ux['accessibility'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "UX - Accessibility",
                "priority": "critical",
                "recommendation": rec
            })
    
    # From market analysis
    if 'platform_optimization' in market:
        print("📊 Aggregating results platform_optimization ...")
        recs = market['platform_optimization'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Market - Platform",
                "priority": "high",
                "recommendation": rec
            })
    
    if 'engagement_prediction' in market:
        print("📊 Aggregating results engagement_prediction ...")
        tips = market['engagement_prediction'].get('optimization_tips', [])
        for tip in tips[:3]:
            all_recommendations.append({
                "source": "Market - Engagement",
                "priority": "medium",
                "recommendation": tip
            })

    # From conversion analysis
    if 'cta' in conversion:
        recs = conversion['cta'].get('recommendations', [])
        for rec in recs[:3]:
            all_recommendations.append({
                "source": "Conversion - CTA",
                "priority": "high",
                "recommendation": rec
            })

    if 'copy' in conversion:
        recs = conversion['copy'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Conversion - Copy",
                "priority": "medium",
                "recommendation": rec
            })

    if 'funnel_fit' in conversion:
        recs = conversion['funnel_fit'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Conversion - Funnel",
                "priority": "medium",
                "recommendation": rec
            })

    # From brand analysis
    if 'logo_usage' in brand:
        recs = brand['logo_usage'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Brand - Logo",
                "priority": "high",
                "recommendation": rec
            })

    if 'palette_alignment' in brand:
        recs = brand['palette_alignment'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Brand - Palette",
                "priority": "medium",
                "recommendation": rec
            })

    if 'typography_alignment' in brand:
        recs = brand['typography_alignment'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Brand - Typography",
                "priority": "medium",
                "recommendation": rec
            })

    if 'tone_voice' in brand:
        recs = brand['tone_voice'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Brand - Tone",
                "priority": "medium",
                "recommendation": rec
            })
    
    # Limit to top 10 recommendations
    prioritized_recommendations = all_recommendations[:10]
    
    # Build final report
    state['final_report'] = {
        "overall_score": round(overall_score, 1),
        "agent_scores": {
            "visual": round(visual_score, 1),
            "ux": round(ux_score, 1),
            "market": round(market_score, 1),
            "conversion": round(conversion_score, 1),
            "brand": round(brand_score, 1)
        },
        "top_recommendations": prioritized_recommendations,
        "detailed_findings": {
            "visual": visual,
            "ux": ux,
            "market": market,
            "conversion": conversion,
            "brand": brand
        },
        "agent_errors": agent_errors,
        "metadata": state.get('image_metadata', {}),
        "platform": state.get('platform', 'Unknown'),
        "creative_type": state.get('creative_type', 'General'),
        "timestamp": datetime.now().isoformat(),
        "model_used": state.get('model_used', 'Unknown')
    }
    
    state['current_step'] = state.get('current_step', 0) + 1
    print("📊 Aggregating results completed!")
    return state


def _maybe_skip(agent_name, output_key, agent_fn):
    """
    Wrap agent to allow skipping when disabled by user selection.
    """
    def runner(state):
        enabled = state.get("enabled_agents", [])
        if enabled and agent_name not in enabled:
            state[output_key] = {"error": "skipped_by_user"}
            state['current_step'] = state.get('current_step', 0) + 1
            return state
        return agent_fn(state)
    return runner


def create_orchestration_graph(faiss_index, metadata):
    """
    Function 5.2: Build LangGraph workflow
    
    Args:
        faiss_index: FAISS index for RAG
        metadata: Pattern metadata
    
    Returns:
        Compiled LangGraph application
    """
    from components.agents import visual_analysis_agent, ux_critique_agent, market_research_agent, conversion_optimization_agent, brand_consistency_agent
    
    # Initialize graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes (agents)
    workflow.add_node(
        "visual_agent",
        _maybe_skip(
            "visual",
            "visual_analysis",
            lambda state: visual_analysis_agent(state, faiss_index, metadata, state.get("top_k", 3))
        )
    )
    workflow.add_node(
        "ux_agent",
        _maybe_skip(
            "ux",
            "ux_analysis",
            lambda state: ux_critique_agent(state, faiss_index, metadata, state.get("top_k", 3))
        )
    )
    workflow.add_node(
        "market_agent",
        _maybe_skip(
            "market",
            "market_analysis",
            lambda state: market_research_agent(state, faiss_index, metadata, state.get("top_k", 3))
        )
    )
    workflow.add_node(
        "conversion_agent",
        _maybe_skip(
            "conversion",
            "conversion_analysis",
            lambda state: conversion_optimization_agent(state, faiss_index, metadata, state.get("top_k", 3))
        )
    )
    workflow.add_node(
        "brand_agent",
        _maybe_skip(
            "brand",
            "brand_analysis",
            lambda state: brand_consistency_agent(state, faiss_index, metadata, state.get("top_k", 3))
        )
    )
    workflow.add_node("aggregator", aggregate_results_node)
    
    # Define edges (sequential flow)
    workflow.set_entry_point("visual_agent")
    workflow.add_edge("visual_agent", "ux_agent")
    workflow.add_edge("ux_agent", "market_agent")
    workflow.add_edge("market_agent", "conversion_agent")
    workflow.add_edge("conversion_agent", "brand_agent")
    workflow.add_edge("brand_agent", "aggregator")
    workflow.add_edge("aggregator", END)
    
    # Compile
    app = workflow.compile()
    
    print("✅ LangGraph workflow created")
    return app


def execute_analysis_workflow(graph, initial_state, progress_callback=None):
    """
    Function 5.3: Execute LangGraph workflow with progress tracking
    
    Args:
        graph: Compiled LangGraph application
        initial_state: Initial analysis state
        progress_callback: Function to call for progress updates
    
    Returns:
        dict: Final state after all agents complete
    """
    step_names = ["Visual Analysis", "UX Critique", "Market Research", "Conversion Optimization", "Brand Consistency", "Aggregating Results"]
    total_steps = len(step_names)
    
    try:
        # Execute graph
        final_state = None
        current_step = 0
        
        for output in graph.stream(initial_state):
            # Update progress
            if progress_callback and current_step < len(step_names):
                progress_callback(
                    current_step + 1,
                    total_steps,
                    f"🔄 {step_names[current_step]}..."
                )
            
            # LangGraph stream yields dicts keyed by node name; ignore __end__ events
            if isinstance(output, dict):
                for key in ['aggregator', 'market_agent', 'ux_agent', 'visual_agent']:
                    if key in output:
                        final_state = output[key]
                        break
            
            current_step += 1
        
        return final_state or {}

    except Exception as e:
        print(f"❌ Error in workflow execution: {e}")
        return {
            "error": str(e),
            "final_report": {
                "overall_score": 0,
                "agent_scores": {"visual": 0, "ux": 0, "market": 0},
                "top_recommendations": [],
                "error_message": str(e)
            }
        }
