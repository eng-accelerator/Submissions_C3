"""
Multi-Agent AI Deep Researcher with Groq (FREE & FAST)
Install: pip install streamlit langchain langchain-groq langgraph tavily-python python-dotenv
Run: streamlit run app.py

Get Groq API Key: https://console.groq.com/keys (FREE!)
"""

import streamlit as st
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Dict, Any
import operator
import json
import re

# LangChain with Groq (Llama 3)
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from tavily import TavilyClient

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Deep Researcher",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

# Initialize LLM and tools
@st.cache_resource
def init_tools():
    """Initialize Groq LLM and Tavily search"""
    
    # Groq with Llama 3 (FREE & SUPER FAST)
    llm = ChatGroq(
        # model="llama-3.1-70b-versatile",
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_tokens=1500
    )
    
    # Tavily search
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    return llm, tavily

try:
    llm, tavily_client = init_tools()
    api_status = "✅ APIs Connected"
except Exception as e:
    st.error(f"❌ API Connection Error: {str(e)}")
    st.info("💡 Make sure your .env file has:\nGROQ_API_KEY=gsk_...\nTAVILY_API_KEY=tvly_...")
    st.stop()


# ============= AGENT STATE =============

class AgentState(TypedDict):
    """State shared between all agents"""
    query: str
    research_plan: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    insights: Dict[str, Any]
    final_report: str
    messages: Annotated[List[str], operator.add]


# ============= AGENT DEFINITIONS =============

class ResearchPlannerAgent:
    """Agent 1: Plans the research strategy"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def invoke(self, state: AgentState) -> AgentState:
        """Create research plan"""
        
        prompt = f"""You are a Research Planning Agent. Create a comprehensive research strategy.

Query: {state['query']}

Create a JSON response with:
1. "topics": List of 3-5 key research topics
2. "search_queries": List of 5-7 specific search queries to find relevant information
3. "source_types": Types of sources needed (academic, news, reports, statistics, etc.)
4. "research_depth": Depth level (surface, moderate, comprehensive)

Return ONLY valid JSON, no markdown formatting or extra text.

Example format:
{{
    "topics": ["Topic 1", "Topic 2", "Topic 3"],
    "search_queries": ["Query 1", "Query 2"],
    "source_types": ["academic", "news"],
    "research_depth": "comprehensive"
}}"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            
            # Extract JSON from response
            response_text = response.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                research_plan = json.loads(json_match.group())
            else:
                # Fallback plan
                research_plan = {
                    "topics": [state['query']],
                    "search_queries": [state['query']],
                    "source_types": ["web"],
                    "research_depth": "moderate"
                }
            
            state['research_plan'] = research_plan
            state['messages'].append(f"✓ Research plan created with {len(research_plan['search_queries'])} queries")
            
        except Exception as e:
            state['messages'].append(f"⚠ Planning error: {str(e)}")
            state['research_plan'] = {
                "topics": [state['query']],
                "search_queries": [state['query']],
                "source_types": ["web"],
                "research_depth": "basic"
            }
        
        return state


class WebSearchAgent:
    """Agent 2: Searches the web using Tavily"""
    
    def __init__(self, tavily_client):
        self.tavily = tavily_client
    
    def invoke(self, state: AgentState) -> AgentState:
        """Execute web searches"""
        
        all_results = []
        search_queries = state['research_plan'].get('search_queries', [state['query']])
        
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, query in enumerate(search_queries[:5]):  # Limit to 5 queries
            status_text.text(f"🔍 Searching: {query[:60]}...")
            
            try:
                # Search with Tavily
                results = self.tavily.search(
                    query=query,
                    max_results=3,
                    search_depth="advanced"
                )
                
                # Process results
                for result in results.get('results', []):
                    all_results.append({
                        'query': query,
                        'title': result.get('title', 'Untitled'),
                        'url': result.get('url', ''),
                        'content': result.get('content', '')[:1000],  # Limit content
                        'score': result.get('score', 0)
                    })
                    
            except Exception as e:
                state['messages'].append(f"⚠ Search failed for '{query[:30]}': {str(e)}")
            
            # Update progress
            progress_bar.progress((i + 1) / min(len(search_queries), 5))
        
        # Clean up progress indicators
        progress_bar.empty()
        status_text.empty()
        
        state['search_results'] = all_results
        state['messages'].append(f"✓ Found {len(all_results)} sources from Tavily")
        
        return state


class AnalysisAgent:
    """Agent 3: Analyzes search results critically"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def invoke(self, state: AgentState) -> AgentState:
        """Analyze findings"""
        
        # Prepare context from search results
        context = "\n\n".join([
            f"Source {i+1}: {r['title']}\n{r['content'][:400]}"
            for i, r in enumerate(state['search_results'][:10])
        ])
        
        prompt = f"""You are a Critical Analysis Agent. Analyze these research findings.

Original Query: {state['query']}

Research Findings:
{context}

Provide a JSON analysis with:
1. "key_findings": List of 5-7 most important findings (be specific)
2. "contradictions": Any conflicting information found (or "None identified")
3. "data_quality": Assessment of source reliability (1-2 sentences)
4. "confidence_level": Overall confidence - must be one of: "low", "medium", or "high"
5. "gaps": What information is missing or needs further research

Return ONLY valid JSON, no markdown.

Example:
{{
    "key_findings": ["Finding 1", "Finding 2"],
    "contradictions": "None identified",
    "data_quality": "Sources appear reliable",
    "confidence_level": "high",
    "gaps": "More recent data needed"
}}"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {
                    "key_findings": ["Analysis completed from available sources"],
                    "contradictions": "None identified",
                    "data_quality": "Moderate quality sources",
                    "confidence_level": "medium",
                    "gaps": "Limited data available"
                }
            
            state['analysis'] = analysis
            state['messages'].append(f"✓ Analysis complete: {len(analysis.get('key_findings', []))} key findings")
            
        except Exception as e:
            state['messages'].append(f"⚠ Analysis error: {str(e)}")
            state['analysis'] = {
                "key_findings": ["Analysis encountered errors"],
                "contradictions": "Unable to determine",
                "data_quality": "Unknown",
                "confidence_level": "low",
                "gaps": "Analysis incomplete"
            }
        
        return state


class InsightGenerationAgent:
    """Agent 4: Generates insights and recommendations"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def invoke(self, state: AgentState) -> AgentState:
        """Generate actionable insights"""
        
        prompt = f"""You are an Insight Generation Agent. Synthesize insights from the analysis.

Original Query: {state['query']}

Key Findings: {state['analysis'].get('key_findings', [])}

Generate a JSON response with:
1. "main_insights": 3-5 key takeaways (be specific and actionable)
2. "trends": Emerging patterns or trends (2-4 items)
3. "implications": Real-world implications (2-3 items)
4. "recommendations": 3-5 actionable recommendations
5. "future_research": Areas needing more investigation (2-3 items)

Return ONLY valid JSON, no markdown.

Example:
{{
    "main_insights": ["Insight 1", "Insight 2"],
    "trends": ["Trend 1", "Trend 2"],
    "implications": ["Implication 1"],
    "recommendations": ["Recommendation 1"],
    "future_research": ["Area 1"]
}}"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            
            if json_match:
                insights = json.loads(json_match.group())
            else:
                insights = {
                    "main_insights": ["Insights generated from available data"],
                    "trends": ["Trends identified"],
                    "implications": ["Various implications noted"],
                    "recommendations": ["Further analysis recommended"],
                    "future_research": ["Additional research suggested"]
                }
            
            state['insights'] = insights
            state['messages'].append(f"✓ Generated {len(insights.get('main_insights', []))} insights")
            
        except Exception as e:
            state['messages'].append(f"⚠ Insight generation error: {str(e)}")
            state['insights'] = {
                "main_insights": ["Error generating insights"],
                "trends": ["Unable to identify trends"],
                "implications": ["Analysis incomplete"],
                "recommendations": ["Retry analysis"],
                "future_research": ["Complete analysis needed"]
            }
        
        return state


class ReportBuilderAgent:
    """Agent 5: Compiles comprehensive report"""
    
    def __init__(self, llm):
        self.llm = llm
    
    def invoke(self, state: AgentState) -> AgentState:
        """Build final research report"""
        
        prompt = f"""You are a Report Builder Agent. Create a comprehensive executive summary.

Query: {state['query']}

Research Plan: {state['research_plan']}
Key Findings: {state['analysis'].get('key_findings', [])}
Insights: {state['insights'].get('main_insights', [])}
Recommendations: {state['insights'].get('recommendations', [])}

Write a professional executive summary (4-6 well-developed paragraphs) that:

1. Opens with the research question and brief methodology
2. Presents key findings with specific evidence from sources
3. Discusses critical insights and emerging trends
4. Provides actionable recommendations based on the analysis
5. Concludes with implications and future research directions

Use clear, academic prose. Be specific and evidence-based. Write in full paragraphs, not bullet points."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state['final_report'] = response.content
            state['messages'].append("✓ Final report compiled")
            
        except Exception as e:
            state['messages'].append(f"⚠ Report building error: {str(e)}")
            state['final_report'] = f"Error generating report: {str(e)}"
        
        return state


# ============= LANGGRAPH WORKFLOW =============

@st.cache_resource
def create_research_graph():
    """Create and compile the agent workflow graph"""
    
    # Initialize agents
    planner = ResearchPlannerAgent(llm)
    searcher = WebSearchAgent(tavily_client)
    analyzer = AnalysisAgent(llm)
    insight_gen = InsightGenerationAgent(llm)
    reporter = ReportBuilderAgent(llm)
    
    # Create workflow graph
    workflow = StateGraph(AgentState)
    
    # Add agent nodes
    workflow.add_node("plan", planner.invoke)
    workflow.add_node("search", searcher.invoke)
    workflow.add_node("analyze", analyzer.invoke)
    workflow.add_node("insights", insight_gen.invoke)
    workflow.add_node("report", reporter.invoke)
    
    # Define workflow edges (sequential execution)
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "search")
    workflow.add_edge("search", "analyze")
    workflow.add_edge("analyze", "insights")
    workflow.add_edge("insights", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()


# ============= STREAMLIT UI =============

st.title("🧠 Multi-Agent AI Deep Researcher")
st.markdown("*Powered by Groq Llama 3.1 (FREE & FAST) + Tavily Search + LangGraph*")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Info")
    st.info(api_status)
    
    st.markdown("**Tech Stack:**")
    st.code("• Groq Llama 3.1 70B\n• Tavily Search API\n• LangGraph\n• Streamlit")
    
    st.markdown("---")
    st.markdown("**Agent Pipeline:**")
    agents = [
        "1. 🎯 Research Planner",
        "2. 🔍 Web Search",
        "3. 📊 Critical Analysis", 
        "4. 💡 Insight Generator",
        "5. 📝 Report Builder"
    ]
    for agent in agents:
        st.markdown(agent)
    
    st.markdown("---")
    st.markdown("**Cost per Query:** $0.00 🎉")
    st.markdown("**Speed:** ⚡ Ultra-fast!")

# Main interface
st.markdown("### Enter Your Research Query")

query = st.text_input(
    "What would you like to research?",
    value=st.session_state.current_query,
    placeholder="e.g., Latest developments in quantum computing and their impact",
    key="query_input",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([2, 1, 3])
with col1:
    research_button = st.button("🔬 Start Research", type="primary", use_container_width=True)
with col2:
    if st.session_state.results:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.results = None
            st.session_state.agent_logs = []
            st.rerun()

# Execute research
if research_button and query:
    st.session_state.agent_logs = []
    st.session_state.results = None
    
    with st.spinner("🤖 AI Agents are researching..."):
        try:
            # Initialize state
            initial_state = {
                "query": query,
                "research_plan": {},
                "search_results": [],
                "analysis": {},
                "insights": {},
                "final_report": "",
                "messages": []
            }
            
            # Create progress container
            progress_container = st.container()
            
            with progress_container:
                st.info("🎯 Stage 1/5: Planning research strategy...")
                
                # Execute workflow
                graph = create_research_graph()
                final_state = graph.invoke(initial_state)
                
                # Store results
                st.session_state.results = final_state
                st.session_state.agent_logs = final_state['messages']
            
            st.success("✅ Research complete! Scroll down to view results.")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error during research: {str(e)}")
            st.info("💡 Tip: Check your API keys in the .env file")

# Display results
if st.session_state.results:
    results = st.session_state.results
    
    # Agent activity logs
    with st.expander("🤖 Agent Activity Logs", expanded=False):
        for log in st.session_state.agent_logs:
            st.text(log)
    
    st.markdown("---")
    
    # Metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sources Found", len(results.get('search_results', [])))
    with col2:
        confidence = results.get('analysis', {}).get('confidence_level', 'medium')
        st.metric("Confidence Level", confidence.title())
    with col3:
        st.metric("Key Findings", len(results.get('analysis', {}).get('key_findings', [])))
    
    st.markdown("---")
    
    # Research Plan
    st.subheader("🎯 Research Strategy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Topics Researched:**")
        for topic in results.get('research_plan', {}).get('topics', []):
            st.markdown(f"• {topic}")
    
    with col2:
        st.markdown("**Search Queries Used:**")
        for query_item in results.get('research_plan', {}).get('search_queries', [])[:5]:
            st.markdown(f"• {query_item}")
    
    st.markdown("---")
    
    # Sources
    st.subheader("📚 Research Sources")
    st.caption(f"Retrieved {len(results.get('search_results', []))} sources via Tavily")
    
    for i, source in enumerate(results.get('search_results', [])[:10], 1):
        with st.expander(f"📄 Source {i}: {source.get('title', 'Untitled')}"):
            st.markdown(f"**URL:** [{source.get('url', 'N/A')}]({source.get('url', '#')})")
            st.markdown(f"**Relevance Score:** {source.get('score', 0):.2%}")
            st.markdown(f"**Content Preview:**")
            st.text(source.get('content', 'No content available')[:500] + "...")
    
    st.markdown("---")
    
    # Analysis
    st.subheader("🔬 Critical Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Key Findings:**")
        for finding in results.get('analysis', {}).get('key_findings', []):
            st.markdown(f"• {finding}")
    
    with col2:
        st.info(f"**Data Quality:**\n{results.get('analysis', {}).get('data_quality', 'N/A')}")
        
        contradictions = results.get('analysis', {}).get('contradictions', 'None')
        if contradictions.lower() != 'none' and contradictions.lower() != 'none identified':
            st.warning(f"**Contradictions:**\n{contradictions}")
        
        gaps = results.get('analysis', {}).get('gaps', 'None')
        if gaps.lower() != 'none':
            st.error(f"**Gaps:**\n{gaps}")
    
    st.markdown("---")
    
    # Insights
    st.subheader("💡 Insights & Recommendations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Main Insights", "Trends", "Recommendations", "Future Research"])
    
    with tab1:
        for insight in results.get('insights', {}).get('main_insights', []):
            st.markdown(f"✓ {insight}")
    
    with tab2:
        for trend in results.get('insights', {}).get('trends', []):
            st.markdown(f"📈 {trend}")
    
    with tab3:
        for rec in results.get('insights', {}).get('recommendations', []):
            st.markdown(f"→ {rec}")
    
    with tab4:
        for area in results.get('insights', {}).get('future_research', []):
            st.markdown(f"🔍 {area}")
    
    st.markdown("---")
    
    # Executive Summary
    st.subheader("📝 Executive Summary")
    st.markdown(results.get('final_report', 'No report generated'))
    
    st.markdown("---")
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        # Download JSON
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            label="📥 Download Full Report (JSON)",
            data=json_data,
            file_name=f"research_report_{query[:30].replace(' ', '_')}.json",
            mime="application/json"
        )
    
    with col2:
        # Download text summary
        text_report = f"""RESEARCH REPORT
================

Query: {query}

EXECUTIVE SUMMARY:
{results.get('final_report', '')}

KEY FINDINGS:
{chr(10).join(['• ' + f for f in results.get('analysis', {}).get('key_findings', [])])}

RECOMMENDATIONS:
{chr(10).join(['• ' + r for r in results.get('insights', {}).get('recommendations', [])])}

Sources: {len(results.get('search_results', []))} sources analyzed
"""
        st.download_button(
            label="📄 Download Summary (TXT)",
            data=text_report,
            file_name=f"research_summary_{query[:30].replace(' ', '_')}.txt",
            mime="text/plain"
        )

# Example queries
if not st.session_state.results:
    st.markdown("---")
    st.subheader("💡 Example Research Queries")
    
    examples = [
        "Latest breakthroughs in quantum computing and their practical applications",
        "Impact of artificial intelligence on healthcare diagnostics in 2024",
        "Current state of renewable energy storage technology",
        "Ethical considerations in gene editing and CRISPR technology",
        "Effects of remote work on employee productivity and mental health",
        "Recent developments in nuclear fusion energy research"
    ]
    
    cols = st.columns(2)
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            if st.button(example, key=f"example_{idx}", use_container_width=True):
                st.session_state.current_query = example
                st.rerun()

# Footer
st.markdown("---")
st.caption("Built with ❤️ using Groq Llama 3.1 (FREE), Tavily Search, LangGraph & Streamlit")