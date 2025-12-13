from langgraph.graph import StateGraph, END
from graph.state import AgentState
from agents.planner import PlannerAgent
from agents.retriever import RetrieverAgent
from agents.analyst import AnalystAgent
from agents.insight import InsightAgent
from agents.reflection import ReflectionAgent
from agents.reporter import ReportAgent
from agents.credibility import CredibilityAgent
from utils.logging import logger

# Initialize Agents
planner = PlannerAgent()
retriever = RetrieverAgent()
analyst = AnalystAgent()
insight = InsightAgent()
reflector = ReflectionAgent()
credibility = CredibilityAgent()
reporter = ReportAgent()

def plan_node(state: AgentState):
    logger.info("--- QUERY UNDERSTANDING / PLAN NODE ---")
    uploaded_files = state.get("uploaded_files", [])
    file_sources = [f.get("source", "") for f in uploaded_files if isinstance(f, dict)]
    plan = planner.create_plan(state.get("task", ""), state.get("discipline", ""), file_sources)
    if plan:
        logger.info(f"Identified domains: {plan.primary_domains if hasattr(plan, 'primary_domains') else 'N/A'}")
        logger.info(f"Agent routing: {plan.agent_routing if hasattr(plan, 'agent_routing') else 'N/A'}")
    return {
        "plan": plan.dict() if plan else {}, 
        "research_scope": plan.scope_and_assumptions.dict() if plan and hasattr(plan, "scope_and_assumptions") else {},
        "iteration_count": 0
    }

def retrieve_node(state: AgentState):
    logger.info("--- RETRIEVER AGENT NODE ---")
    current_plan = state.get("plan", {})
    # Get queries to run (either initial sub_queries or follow_ups)
    # usage logic: if iteration > 0, use follow_ups from reflection, else use sub_queries
    
    queries_to_run = []
    if state.get("iteration_count", 0) == 0:
        sub_queries = current_plan.get("sub_queries", [])
        queries_to_run = [sq.get("query", "") for sq in sub_queries if isinstance(sq, dict)]
    else:
        reflection = state.get("reflection", {})
        queries_to_run = reflection.get("follow_up_queries", [])

    new_findings = []
    # Limit queries for speed in demo
    for q in queries_to_run[:3]:
        if not q:
            continue
        try:
            results = retriever.retrieve(q, state.get("findings", []), state.get("uploaded_files", []))
            # Analyze immediately or collect? Let's analyze immediately to get structured finding
            analysis = analyst.analyze(q, results)
            new_findings.append({
                "query": q,
                "raw_results": results,
                "summary": analysis.get("summary", ""),
                "key_findings": analysis.get("key_findings", []),
                "contradictions": analysis.get("contradictions", []),
                "validations": analysis.get("validations", []),
                "uncertainties": analysis.get("uncertainties", [])
            })
        except Exception as e:
            logger.error(f"Error in retrieve_node for query '{q}': {e}")
            new_findings.append({
                "query": q,
                "raw_results": [],
                "summary": f"Error processing query: {str(e)}",
                "key_findings": []
            })
    
    return {"findings": new_findings}

def insight_node(state: AgentState):
    logger.info("--- INSIGHT GENERATOR AGENT NODE ---")
    findings = state.get("findings", [])
    discipline = state.get("discipline", "")
    insight_result = insight.generate_insights(findings, discipline)
    # insight_result is now a dict with hypotheses, insights, reasoning_chains, connections, implications, trends, research_questions
    return {
        "insights": insight_result.get("insights", []),
        "hypotheses": insight_result.get("hypotheses", []),
        "reasoning_chains": insight_result.get("reasoning_chains", []),
        "connections": insight_result.get("connections", []),
        "implications": insight_result.get("implications", []),
        "trends": insight_result.get("trends", []),
        "research_questions": insight_result.get("research_questions", [])
    }

def reflect_node(state: AgentState):
    logger.info("--- REFLECT NODE ---")
    findings = state.get("findings", [])
    plan = state.get("plan", {})
    reflection = reflector.reflect(findings, plan)
    return {
        "reflection": reflection.dict() if reflection else {}, 
        "iteration_count": state.get("iteration_count", 0) + 1
    }

def report_node(state: AgentState):
    logger.info("--- REPORT BUILDER AGENT NODE ---")
    # Score sources first
    all_sources = []
    findings = state.get("findings", [])
    for f in findings:
        if isinstance(f, dict):
            raw_results = f.get("raw_results", [])
            for raw in raw_results:
                if isinstance(raw, dict):
                    source = raw.get("source")
                    if source:
                        all_sources.append(source)
    
    scored_sources = credibility.evaluate_sources(list(set(all_sources))) if all_sources else []
    
    plan = state.get("plan", {})
    insights = state.get("insights", [])
    hypotheses = state.get("hypotheses", [])
    reasoning_chains = state.get("reasoning_chains", [])
    connections = state.get("connections", [])
    implications = state.get("implications", [])
    trends = state.get("trends", [])
    research_questions = state.get("research_questions", [])
    research_scope = state.get("research_scope", {})
    report = reporter.generate_report(
        plan, findings, insights, scored_sources, research_scope,
        hypotheses, implications, research_questions, reasoning_chains, connections, trends
    )
    return {"final_report": report, "sources": scored_sources}

def should_continue(state: AgentState):
    reflection = state.get("reflection", {})
    if not isinstance(reflection, dict):
        reflection = {}
    iteration = state.get("iteration_count", 0)
    
    # Max 2 iterations for demo safety
    if iteration >= 2 or reflection.get("is_sufficient", True):
        return "report"
    else:
        return "retrieve"

# Build Graph
workflow = StateGraph(AgentState)

workflow.add_node("planner", plan_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("insight", insight_node)
workflow.add_node("reflector", reflect_node)
workflow.add_node("reporter", report_node)

workflow.set_entry_point("planner")

workflow.add_edge("planner", "retriever")
workflow.add_edge("retriever", "insight")
workflow.add_edge("insight", "reflector")

workflow.add_conditional_edges(
    "reflector",
    should_continue,
    {
        "retrieve": "retriever",
        "report": "reporter"
    }
)

workflow.add_edge("reporter", END)

app_graph = workflow.compile()
