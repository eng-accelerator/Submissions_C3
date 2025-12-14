# graph.py
from langgraph.graph import StateGraph, END
from state import ResearchState

from agents.youtube_agent import youtube_agent_node
from agents.retriever import retriever_node
from agents.structurer import structurer_node
from agents.analysis import analysis_node
from agents.factcheck import factcheck_node
from agents.expert import expert_node
from agents.critique import critique_node
from agents.insights import insights_node
from agents.report import report_node


def build_graph(llm, tavily, openrouter_key, youtube_key):
    g = StateGraph(ResearchState)

    g.add_node(
        "youtube",
        lambda s: youtube_agent_node(s, openrouter_key, youtube_key)
    )

    g.add_node("retriever", lambda s: retriever_node(s, llm, tavily))
    g.add_node("structurer", lambda s: structurer_node(s, llm))
    g.add_node("analysis", lambda s: analysis_node(s, llm))
    g.add_node("factcheck", lambda s: factcheck_node(s, llm))
    g.add_node("expert", lambda s: expert_node(s, llm))
    g.add_node("critique", lambda s: critique_node(s, llm))
    g.add_node("insights", lambda s: insights_node(s, llm))
    g.add_node("report", lambda s: report_node(s, llm))

    # 🔹 ENTRY POINT
    g.set_entry_point("youtube")

    # 🔹 FLOW
    g.add_edge("youtube", "retriever")
    g.add_edge("retriever", "structurer")
    g.add_edge("structurer", "analysis")
    g.add_edge("analysis", "factcheck")
    g.add_edge("factcheck", "expert")
    g.add_edge("expert", "critique")
    g.add_edge("critique", "insights")
    g.add_edge("insights", "report")
    g.add_edge("report", END)

    return g.compile()
