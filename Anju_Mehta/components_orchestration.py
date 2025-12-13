components/orchestration.py

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
    image_metadata: dict
    
    # Agent outputs
    visual_analysis: dict
    ux_analysis: dict
    market_analysis: dict
    
    # Final output
    final_report: dict
    
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
    
    visual = state.get('visual_analysis', {})
    ux = state.get('ux_analysis', {})
    market = state.get('market_analysis', {})
    
    # Calculate overall score (weighted average)
    visual_score = visual.get('overall_score', 0)
    ux_score = ux.get('overall_score', 0)
    market_score = market.get('overall_score', 0)
    
    overall_score = (
        visual_score * 0.3 +
        ux_score * 0.4 +
        market_score * 0.3
    )
    
    # Aggregate all recommendations
    all_recommendations = []
    
    # From visual analysis
    if 'color_analysis' in visual:
        recs = visual['color_analysis'].get('recommendations', [])
        for rec in recs[:3]:  # Top 3
            all_recommendations.append({
                "source": "Visual - Color",
                "priority": "high",
                "recommendation": rec
            })
    
    if 'layout_analysis' in visual:
        recs = visual['layout_analysis'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Visual - Layout",
                "priority": "medium",
                "recommendation": rec
            })
    
    if 'typography' in visual:
        recs = visual['typography'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Visual - Typography",
                "priority": "medium",
                "recommendation": rec
            })
    
    # From UX analysis
    if 'usability' in ux:
        recs = ux['usability'].get('recommendations', [])
        for rec in recs[:3]:
            all_recommendations.append({
                "source": "UX - Usability",
                "priority": "high",
                "recommendation": rec
            })
    
    if 'accessibility' in ux:
        recs = ux['accessibility'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "UX - Accessibility",
                "priority": "critical",
                "recommendation": rec
            })
    
    # From market analysis
    if 'platform_optimization' in market:
        recs = market['platform_optimization'].get('recommendations', [])
        for rec in recs[:2]:
            all_recommendations.append({
                "source": "Market - Platform",
                "priority": "high",
                "recommendation": rec
            })
    
    if 'engagement_prediction' in market:
        tips = market['engagement_prediction'].get('optimization_tips', [])
        for tip in tips[:3]:
            all_recommendations.append({
                "source": "Market - Engagement",
                "priority": "medium",
                "recommendation": tip
            })
    
    # Limit to top 10 recommendations
    prioritized_recommendations = all_recommendations[:10]
    
    # Build final report
    state['final_report'] = {
        "overall_score": round(overall_score, 1),
        "agent_scores": {
            "visual": round(visual_score, 1),
            "ux": round(ux_score, 1),
            "market": round(market_score, 1)
        },
        "top_recommendations": prioritized_recommendations,
        "detailed_findings": {
            "visual": visual,
            "ux": ux,
            "market": market
        },
        "metadata": state.get('image_metadata', {}),
        "platform": state.get('platform', 'Unknown'),
        "timestamp": datetime.now().isoformat(),
        "model_used": state.get('model_used', 'Unknown')
    }
    
    state['current_step'] = state.get('current_step', 0) + 1
    
    return state


def create_orchestration_graph(faiss_index, metadata):
    """
    Function 5.2: Build LangGraph workflow
    
    Args:
        faiss_index: FAISS index for RAG
        metadata: Pattern metadata
    
    Returns:
        Compiled LangGraph application
    """
    from components.agents import visual_analysis_agent, ux_critique_agent, market_research_agent
    
    # Initialize graph
    workflow = StateGraph(AnalysisState)
    
    # Add nodes (agents)
    workflow.add_node(
        "visual_agent",
        lambda state: visual_analysis_agent(state, faiss_index, metadata)
    )
    workflow.add_node(
        "ux_agent",
        lambda state: ux_critique_agent(state, faiss_index, metadata)
    )
    workflow.add_node(
        "market_agent",
        lambda state: market_research_agent(state, faiss_index, metadata)
    )
    workflow.add_node("aggregator", aggregate_results_node)
    
    # Define edges (sequential flow)
    workflow.set_entry_point("visual_agent")
    workflow.add_edge("visual_agent", "ux_agent")
    workflow.add_edge("ux_agent", "market_agent")
    workflow.add_edge("market_agent", "aggregator")
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
    step_names = ["Visual Analysis", "UX Critique", "Market Research", "Aggregating Results"]
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
            
            final_state = output
            current_step += 1
        
        # Get the last state value (LangGraph returns dict with node names as keys)
        if isinstance(final_state, dict):
            # Extract the actual state from the output
            for key in ['aggregator', 'market_agent', 'ux_agent', 'visual_agent']:
                if key in final_state:
                    final_state,
		return final_state

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