"""
Multi-Agent AI Deep Researcher - ADVANCED VERSION
Features: RAG, PDF Upload, Citations, Streaming, Agent Visualization

Install: pip install streamlit langchain langchain-groq langgraph tavily-python python-dotenv chromadb pypdf sentence-transformers graphviz pydot
Run: streamlit run app.py
"""

import streamlit as st
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Dict, Any
import operator
import json
import re
import time
from datetime import datetime
import base64
from io import BytesIO

# LangChain & LangGraph
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from tavily import TavilyClient

# RAG Components
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter  # ✅ CORRECT
# Replace these imports in appa.py:
from langchain_community.document_loaders import PyPDFLoader  # ← NEW
from langchain_community.vectorstores import Chroma           # ← NEW  
from langchain_community.embeddings import HuggingFaceEmbeddings  # ← NEW


# PDF Processing
from pypdf import PdfReader

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Deep Researcher - Advanced",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'agent_logs' not in st.session_state:
    st.session_state.agent_logs = []
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'citations' not in st.session_state:
    st.session_state.citations = []
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None
if 'uploaded_docs' not in st.session_state:
    st.session_state.uploaded_docs = []
if 'agent_timeline' not in st.session_state:
    st.session_state.agent_timeline = []

# Initialize LLM and tools
@st.cache_resource
def init_tools():
    """Initialize Groq LLM and Tavily search"""
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        groq_api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.7,
        max_tokens=2000
    )
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return llm, tavily

try:
    llm, tavily_client = init_tools()
    api_status = "✅ APIs Connected"
except Exception as e:
    st.error(f"❌ API Connection Error: {str(e)}")
    st.stop()

# Initialize embeddings for RAG
@st.cache_resource
def init_embeddings():
    """Initialize embedding model for RAG"""
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )

embeddings = init_embeddings()


# ============= CITATION TRACKER =============

class CitationTracker:
    """Tracks citations across agents"""
    
    def __init__(self):
        self.citations = []
    
    def add_citation(self, agent_name: str, source_title: str, source_url: str, claim: str):
        """Add a citation"""
        self.citations.append({
            'agent': agent_name,
            'source_title': source_title,
            'source_url': source_url,
            'claim': claim,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_citations_by_agent(self, agent_name: str):
        """Get all citations from specific agent"""
        return [c for c in self.citations if c['agent'] == agent_name]
    
    def get_all_citations(self):
        """Get all citations"""
        return self.citations


# ============= PDF PROCESSOR =============

def process_pdf(uploaded_file):
    """Extract text from PDF and add to vector store"""
    try:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_text(text)
        
        # Create documents
        documents = [
            Document(
                page_content=chunk,
                metadata={
                    'source': uploaded_file.name,
                    'page': i // 3,  # Approximate page number
                    'type': 'uploaded_pdf'
                }
            )
            for i, chunk in enumerate(chunks)
        ]
        
        return documents, text[:500]  # Return docs and preview
        
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return [], ""


# ============= RAG HELPER =============

def add_to_vectorstore(documents: List[Document]):
    """Add documents to vector store"""
    if st.session_state.vectorstore is None:
        # Create new vector store
        st.session_state.vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            collection_name="research_docs"
        )
    else:
        # Add to existing vector store
        st.session_state.vectorstore.add_documents(documents)


def query_vectorstore(query: str, k: int = 3):
    """Query vector store for relevant documents"""
    if st.session_state.vectorstore is None:
        return []
    
    try:
        results = st.session_state.vectorstore.similarity_search(query, k=k)
        return results
    except:
        return []


# ============= AGENT STATE =============

class AgentState(TypedDict):
    """State shared between all agents"""
    query: str
    research_plan: Dict[str, Any]
    search_results: List[Dict[str, Any]]
    rag_results: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    insights: Dict[str, Any]
    final_report: str
    messages: Annotated[List[str], operator.add]
    citations: List[Dict[str, Any]]
    timeline: Annotated[List[Dict[str, Any]], operator.add]


# ============= AGENT DEFINITIONS =============

class ResearchPlannerAgent:
    """Agent 1: Plans the research strategy"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Research Planner"
    
    def invoke(self, state: AgentState) -> AgentState:
        """Create research plan"""
        start_time = time.time()
        
        # Check if RAG has relevant content
        rag_context = ""
        if st.session_state.vectorstore:
            rag_docs = query_vectorstore(state['query'], k=2)
            if rag_docs:
                rag_context = f"\n\nUploaded Documents Context:\n{rag_docs[0].page_content[:300]}"
        
        prompt = f"""You are a Research Planning Agent. Create a comprehensive research strategy.

Query: {state['query']}{rag_context}

Create a JSON response with:
1. "topics": List of 3-5 key research topics
2. "search_queries": List of 5-7 specific search queries
3. "source_types": Types of sources needed
4. "research_depth": Depth level

Return ONLY valid JSON.

Example:
{{
    "topics": ["Topic 1", "Topic 2"],
    "search_queries": ["Query 1", "Query 2"],
    "source_types": ["academic", "news"],
    "research_depth": "comprehensive"
}}"""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            response_text = response.content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                research_plan = json.loads(json_match.group())
            else:
                research_plan = {
                    "topics": [state['query']],
                    "search_queries": [state['query']],
                    "source_types": ["web"],
                    "research_depth": "moderate"
                }
            
            state['research_plan'] = research_plan
            state['messages'].append(f"✓ Research plan created with {len(research_plan['search_queries'])} queries")
            
            # Add to timeline
            state['timeline'].append({
                'agent': self.name,
                'action': 'Planning complete',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            state['messages'].append(f"⚠ Planning error: {str(e)}")
            state['research_plan'] = {
                "topics": [state['query']],
                "search_queries": [state['query']],
                "source_types": ["web"],
                "research_depth": "basic"
            }
        
        return state


class RAGSearchAgent:
    """Agent 1.5: Search uploaded documents"""
    
    def __init__(self):
        self.name = "RAG Search"
    
    def invoke(self, state: AgentState) -> AgentState:
        """Search vector store for relevant content"""
        start_time = time.time()
        
        if st.session_state.vectorstore is None:
            state['rag_results'] = []
            state['messages'].append("ℹ No uploaded documents to search")
            return state
        
        try:
            # Search uploaded documents
            rag_docs = query_vectorstore(state['query'], k=5)
            
            rag_results = []
            for doc in rag_docs:
                rag_results.append({
                    'content': doc.page_content,
                    'source': doc.metadata.get('source', 'Unknown'),
                    'page': doc.metadata.get('page', 0),
                    'type': 'uploaded_document'
                })
            
            state['rag_results'] = rag_results
            state['messages'].append(f"✓ Found {len(rag_results)} relevant sections in uploaded documents")
            
            # Add to timeline
            state['timeline'].append({
                'agent': self.name,
                'action': f'Retrieved {len(rag_results)} document chunks',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            state['messages'].append(f"⚠ RAG search error: {str(e)}")
            state['rag_results'] = []
        
        return state


class WebSearchAgent:
    """Agent 2: Searches the web using Tavily"""
    
    def __init__(self, tavily_client):
        self.tavily = tavily_client
        self.name = "Web Search"
    
    def invoke(self, state: AgentState) -> AgentState:
        """Execute web searches"""
        start_time = time.time()
        
        all_results = []
        search_queries = state['research_plan'].get('search_queries', [state['query']])
        
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        citation_tracker = CitationTracker()
        
        for i, query in enumerate(search_queries[:5]):
            status_text.text(f"🔍 Searching: {query[:60]}...")
            
            try:
                results = self.tavily.search(
                    query=query,
                    max_results=3,
                    search_depth="advanced"
                )
                
                for result in results.get('results', []):
                    result_data = {
                        'query': query,
                        'title': result.get('title', 'Untitled'),
                        'url': result.get('url', ''),
                        'content': result.get('content', '')[:1000],
                        'score': result.get('score', 0)
                    }
                    all_results.append(result_data)
                    
                    # Track citation
                    citation_tracker.add_citation(
                        agent_name=self.name,
                        source_title=result_data['title'],
                        source_url=result_data['url'],
                        claim=f"Retrieved for query: {query}"
                    )
                    
            except Exception as e:
                state['messages'].append(f"⚠ Search failed: {str(e)}")
            
            progress_bar.progress((i + 1) / min(len(search_queries), 5))
        
        progress_bar.empty()
        status_text.empty()
        
        state['search_results'] = all_results
        state['citations'].extend(citation_tracker.get_all_citations())
        state['messages'].append(f"✓ Found {len(all_results)} sources from Tavily")
        
        # Add to timeline
        state['timeline'].append({
            'agent': self.name,
            'action': f'Retrieved {len(all_results)} web sources',
            'duration': round(time.time() - start_time, 2),
            'timestamp': datetime.now().isoformat()
        })
        
        return state


class AnalysisAgent:
    """Agent 3: Analyzes search results critically"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Critical Analysis"
    
    def invoke(self, state: AgentState) -> AgentState:
        """Analyze findings"""
        start_time = time.time()
        
        # Combine web and RAG results
        web_context = "\n\n".join([
            f"Source {i+1}: {r['title']}\n{r['content'][:400]}"
            for i, r in enumerate(state['search_results'][:10])
        ])
        
        rag_context = ""
        if state.get('rag_results'):
            rag_context = "\n\nUploaded Documents:\n" + "\n\n".join([
                f"Doc {i+1}: {r['content'][:300]}"
                for i, r in enumerate(state['rag_results'][:3])
            ])
        
        prompt = f"""You are a Critical Analysis Agent.

Query: {state['query']}

Web Sources:
{web_context}
{rag_context}

Provide JSON analysis with:
1. "key_findings": 5-7 findings
2. "contradictions": conflicts found
3. "data_quality": reliability assessment
4. "confidence_level": "low", "medium", or "high"
5. "gaps": missing information

Return ONLY valid JSON."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                analysis = {
                    "key_findings": ["Analysis completed"],
                    "contradictions": "None identified",
                    "data_quality": "Moderate",
                    "confidence_level": "medium",
                    "gaps": "Limited data"
                }
            
            state['analysis'] = analysis
            state['messages'].append(f"✓ Analysis complete: {len(analysis.get('key_findings', []))} findings")
            
            # Add to timeline
            state['timeline'].append({
                'agent': self.name,
                'action': 'Analysis completed',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            state['messages'].append(f"⚠ Analysis error: {str(e)}")
            state['analysis'] = {
                "key_findings": ["Error"],
                "contradictions": "Unknown",
                "data_quality": "Unknown",
                "confidence_level": "low",
                "gaps": "Analysis incomplete"
            }
        
        return state


class InsightGenerationAgent:
    """Agent 4: Generates insights"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Insight Generator"
    
    def invoke(self, state: AgentState) -> AgentState:
        """Generate insights"""
        start_time = time.time()
        
        prompt = f"""You are an Insight Generation Agent.

Query: {state['query']}
Findings: {state['analysis'].get('key_findings', [])}

Generate JSON with:
1. "main_insights": 3-5 takeaways
2. "trends": 2-4 patterns
3. "implications": 2-3 implications
4. "recommendations": 3-5 recommendations
5. "future_research": 2-3 areas

Return ONLY valid JSON."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            
            if json_match:
                insights = json.loads(json_match.group())
            else:
                insights = {
                    "main_insights": ["Insights generated"],
                    "trends": ["Trends identified"],
                    "implications": ["Implications noted"],
                    "recommendations": ["Recommendations provided"],
                    "future_research": ["Further study needed"]
                }
            
            state['insights'] = insights
            state['messages'].append(f"✓ Generated {len(insights.get('main_insights', []))} insights")
            
            # Add to timeline
            state['timeline'].append({
                'agent': self.name,
                'action': 'Insights generated',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            state['messages'].append(f"⚠ Insight error: {str(e)}")
            state['insights'] = {
                "main_insights": ["Error"],
                "trends": ["Unknown"],
                "implications": ["Unknown"],
                "recommendations": ["Retry"],
                "future_research": ["Complete analysis"]
            }
        
        return state


class ReportBuilderAgent:
    """Agent 5: Builds final report"""
    
    def __init__(self, llm):
        self.llm = llm
        self.name = "Report Builder"
    
    def invoke(self, state: AgentState) -> AgentState:
        """Build report"""
        start_time = time.time()
        
        prompt = f"""You are a Report Builder Agent.

Query: {state['query']}
Findings: {state['analysis'].get('key_findings', [])}
Insights: {state['insights'].get('main_insights', [])}

Write a professional executive summary (4-6 paragraphs):
1. Research question and methodology
2. Key findings with evidence
3. Critical insights and trends
4. Actionable recommendations
5. Implications and future directions

Use academic prose, be specific and evidence-based."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            state['final_report'] = response.content
            state['messages'].append("✓ Final report compiled")
            
            # Add to timeline
            state['timeline'].append({
                'agent': self.name,
                'action': 'Report compiled',
                'duration': round(time.time() - start_time, 2),
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            state['messages'].append(f"⚠ Report error: {str(e)}")
            state['final_report'] = f"Error: {str(e)}"
        
        return state


# ============= LANGGRAPH WORKFLOW =============

@st.cache_resource
def create_research_graph():
    """Create agent workflow"""
    
    planner = ResearchPlannerAgent(llm)
    rag_searcher = RAGSearchAgent()
    web_searcher = WebSearchAgent(tavily_client)
    analyzer = AnalysisAgent(llm)
    insight_gen = InsightGenerationAgent(llm)
    reporter = ReportBuilderAgent(llm)
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node("plan", planner.invoke)
    workflow.add_node("rag_search", rag_searcher.invoke)
    workflow.add_node("web_search", web_searcher.invoke)
    workflow.add_node("analyze", analyzer.invoke)
    workflow.add_node("insights", insight_gen.invoke)
    workflow.add_node("report", reporter.invoke)
    
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "rag_search")
    workflow.add_edge("rag_search", "web_search")
    workflow.add_edge("web_search", "analyze")
    workflow.add_edge("analyze", "insights")
    workflow.add_edge("insights", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()


# ============= AGENT VISUALIZATION =============

def create_agent_visualization():
    """Create visual workflow diagram"""
    
    workflow_html = """
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white;">
        <h3 style="text-align: center; margin-bottom: 20px;">Agent Workflow Pipeline</h3>
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
            <div style="text-align: center; margin: 10px;">
                <div style="background: white; color: #667eea; padding: 15px; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto;">1</div>
                <p style="margin-top: 10px;">Planner</p>
            </div>
            <div style="font-size: 30px; margin: 10px;">→</div>
            <div style="text-align: center; margin: 10px;">
                <div style="background: white; color: #667eea; padding: 15px; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto;">2</div>
                <p style="margin-top: 10px;">RAG Search</p>
            </div>
            <div style="font-size: 30px; margin: 10px;">→</div>
            <div style="text-align: center; margin: 10px;">
                <div style="background: white; color: #667eea; padding: 15px; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto;">3</div>
                <p style="margin-top: 10px;">Web Search</p>
            </div>
            <div style="font-size: 30px; margin: 10px;">→</div>
            <div style="text-align: center; margin: 10px;">
                <div style="background: white; color: #667eea; padding: 15px; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto;">4</div>
                <p style="margin-top: 10px;">Analyzer</p>
            </div>
            <div style="font-size: 30px; margin: 10px;">→</div>
            <div style="text-align: center; margin: 10px;">
                <div style="background: white; color: #667eea; padding: 15px; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto;">5</div>
                <p style="margin-top: 10px;">Insights</p>
            </div>
            <div style="font-size: 30px; margin: 10px;">→</div>
            <div style="text-align: center; margin: 10px;">
                <div style="background: white; color: #667eea; padding: 15px; border-radius: 50%; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; font-weight: bold; margin: 0 auto;">6</div>
                <p style="margin-top: 10px;">Reporter</p>
            </div>
        </div>
    </div>
    """
    return workflow_html


# ============= STREAMLIT UI =============

st.title("🧠 Multi-Agent AI Deep Researcher - Advanced")
st.markdown("*Features: RAG • PDF Upload • Citations • Agent Visualization*")

# Sidebar
with st.sidebar:
    st.header("⚙️ System Info")
    st.info(api_status)
    
    st.markdown("---")
    st.subheader("📤 Upload Research Documents")
    
    uploaded_files = st.file_uploader(
        "Upload PDFs for RAG",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload research papers, reports, or documents to enhance research"
    )
    
    if uploaded_files:
        if st.button("Process PDFs", type="primary"):
            with st.spinner("Processing PDFs..."):
                all_docs = []
                for uploaded_file in uploaded_files:
                    docs, preview = process_pdf(uploaded_file)
                    if docs:
                        all_docs.extend(docs)
                        st.session_state.uploaded_docs.append({
                            'name': uploaded_file.name,
                            'preview': preview,
                            'chunks': len(docs)
                        })
                
                if all_docs:
                    add_to_vectorstore(all_docs)
                    st.success(f"✅ Processed {len(uploaded_files)} PDFs ({len(all_docs)} chunks)")
    
    # Show uploaded docs
    if st.session_state.uploaded_docs:
        st.markdown("---")
        st.subheader("📚 Uploaded Documents")
        for doc in st.session_state.uploaded_docs:
            with st.expander(doc['name']):
                st.caption(f"Chunks: {doc['chunks']}")
                st.text(doc['preview'][:200] + "...")
    
    st.markdown("---")
    st.markdown("**Agent Pipeline:**")
    agents = [
        "1. 🎯 Research Planner",
        "2. 📄 RAG Search",
        "3. 🔍 Web Search",
        "4. 📊 Critical Analysis",
        "5. 💡 Insight Generator",
        "6. 📝 Report Builder"
    ]
    for agent in agents:
        st.markdown(agent)
    
    st.markdown("---")
    st.markdown("**Cost:** $0.00 🎉")

# Main interface
st.markdown("### Enter Your Research Query")

query = st.text_input(
    "Research query",
    value=st.session_state.current_query,
    placeholder="e.g., Impact of AI on healthcare diagnostics",
    key="query_input",
    label_visibility="collapsed"
)

col1, col2 = st.columns([2, 1])
with col1:
    research_button = st.button("🔬 Start Research", type="primary", use_container_width=True)
with col2:
    if st.session_state.results:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.results = None
            st.session_state.agent_logs = []
            st.session_state.citations = []
            st.session_state.agent_timeline = []
            st.rerun()

# Agent Visualization
if not st.session_state.results:
    st.markdown("---")
    st.markdown("### 🎯 Agent Workflow Visualization")
    st.markdown(create_agent_visualization(), unsafe_allow_html=True)

# Execute research
if research_button and query:
    st.session_state.agent_logs = []
    st.session_state.results = None
    st.session_state.citations = []
    st.session_state.agent_timeline = []
    
    with st.spinner("🤖 AI Agents researching..."):
        try:
            initial_state = {
                "query": query,
                "research_plan": {},
                "search_results": [],
                "rag_results": [],
                "analysis": {},
                "insights": {},
                "final_report": "",
                "messages": [],
                "citations": [],
                "timeline": []
            }
            
            st.info("🎯 Executing multi-agent pipeline...")
            
            graph = create_research_graph()
            final_state = graph.invoke(initial_state)
            
            st.session_state.results = final_state
            st.session_state.agent_logs = final_state['messages']
            st.session_state.citations = final_state.get('citations', [])
            st.session_state.agent_timeline = final_state.get('timeline', [])
            
            st.success("✅ Research complete!")
            st.balloons()
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display results
if st.session_state.results:
    results = st.session_state.results
    
    # Agent Timeline
    if st.session_state.agent_timeline:
        with st.expander("⏱️ Agent Execution Timeline", expanded=False):
            for event in st.session_state.agent_timeline:
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**{event['agent']}**")
                with col2:
                    st.markdown(f"{event['action']}")
                with col3:
                    st.markdown(f"`{event['duration']}s`")
            
            total_time = sum(e['duration'] for e in st.session_state.agent_timeline)
            st.info(f"**Total Execution Time:** {total_time:.2f}s")
    
    # Agent Logs
    with st.expander("🤖 Agent Activity Logs", expanded=False):
        for log in st.session_state.agent_logs:
            st.text(log)
    
    st.markdown("---")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Web Sources", len(results.get('search_results', [])))
    with col2:
        st.metric("RAG Sources", len(results.get('rag_results', [])))
    with col3:
        confidence = results.get('analysis', {}).get('confidence_level', 'medium')
        st.metric("Confidence", confidence.title())
    with col4:
        st.metric("Citations", len(st.session_state.citations))
    
    st.markdown("---")
    
    # Research Plan
    st.subheader("🎯 Research Strategy")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Topics:**")
        for topic in results.get('research_plan', {}).get('topics', []):
            st.markdown(f"• {topic}")
    
    with col2:
        st.markdown("**Queries:**")
        for q in results.get('research_plan', {}).get('search_queries', [])[:5]:
            st.markdown(f"• {q}")
    
    st.markdown("---")
    
    # RAG Results
    if results.get('rag_results'):
        st.subheader("📄 Uploaded Document Insights")
        for i, rag in enumerate(results.get('rag_results', [])[:3], 1):
            with st.expander(f"Document {i}: {rag.get('source', 'Unknown')} (Page {rag.get('page', 'N/A')})"):
                st.text(rag.get('content', '')[:500] + "...")
        st.markdown("---")
    
    # Web Sources
    st.subheader("📚 Web Research Sources")
    for i, source in enumerate(results.get('search_results', [])[:10], 1):
        with st.expander(f"Source {i}: {source.get('title', 'Untitled')}"):
            st.markdown(f"**URL:** [{source.get('url', 'N/A')}]({source.get('url', '#')})")
            st.markdown(f"**Relevance:** {source.get('score', 0):.2%}")
            st.text(source.get('content', '')[:500] + "...")
    
    st.markdown("---")
    
    # Citations
    if st.session_state.citations:
        st.subheader("📑 Citations & Sources")
        
        # Group by agent
        citations_by_agent = {}
        for citation in st.session_state.citations:
            agent = citation['agent']
            if agent not in citations_by_agent:
                citations_by_agent[agent] = []
            citations_by_agent[agent].append(citation)
        
        for agent, citations in citations_by_agent.items():
            with st.expander(f"{agent} - {len(citations)} citations"):
                for i, cite in enumerate(citations[:10], 1):
                    st.markdown(f"**{i}.** [{cite['source_title']}]({cite['source_url']})")
                    st.caption(cite['claim'])
        
        st.markdown("---")
    
    # Analysis
    st.subheader("🔬 Critical Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**Key Findings:**")
        for finding in results.get('analysis', {}).get('key_findings', []):
            st.markdown(f"• {finding}")
    
    with col2:
        st.info(f"**Quality:**\n{results.get('analysis', {}).get('data_quality', 'N/A')}")
        
        gaps = results.get('analysis', {}).get('gaps', 'None')
        if gaps and isinstance(gaps, str) and gaps.lower() != 'none':
            st.warning(f"Gaps: {gaps}")
        elif isinstance(gaps, list) and gaps:
            st.warning(f"Gaps: {', '.join(gaps[:3])}...")
        # if gaps.lower() != 'none':
        #     st.warning(f"**Gaps:**\n{gaps}")
    
    st.markdown("---")
    
    ## Critical Analysis section - SAFE VERSION
    # st.subheader("Critical Analysis")
    # col1, col2 = st.columns([2, 1])

    # with col1:
    #     st.markdown("**Key Findings**")
    #     analysis = results.get('analysis', {})
    #     key_findings = analysis.get('keyfindings', [])
    #     if isinstance(key_findings, list):
    #         for finding in key_findings[:5]:  # Limit to 5
    #             st.markdown(f"• {finding}")
    #     else:
    #         st.markdown(f"• {key_findings}")

    # with col2:
    #     st.info(f"**Quality**: {analysis.get('dataquality', 'N/A')}")
        
    #     # SAFE gaps handling
    #     gaps = analysis.get('gaps', [])
    #     if gaps:
    #         if isinstance(gaps, str) and gaps.lower() != 'none':
    #             st.warning(f"**Gaps**: {gaps}")
    #         elif isinstance(gaps, list) and len(gaps) > 0:
    #             st.warning(f"**Gaps** ({len(gaps)}): {', '.join([str(g) for g in gaps[:2]])}...")
    #     else:
    #         st.success("**Complete Analysis** ✅")

    
    # Insights
    st.subheader("💡 Insights & Recommendations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Insights", "Trends", "Recommendations", "Future Research"])
    
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
    st.markdown(results.get('final_report', ''))
    
    st.markdown("---")
    
    # Download
    col1, col2, col3 = st.columns(3)
    
    with col1:
        json_data = json.dumps(results, indent=2, default=str)
        st.download_button(
            "📥 JSON Report",
            json_data,
            f"report_{query[:20]}.json",
            "application/json"
        )
    
    with col2:
        text_report = f"""RESEARCH REPORT
================
Query: {query}

EXECUTIVE SUMMARY:
{results.get('final_report', '')}

KEY FINDINGS:
{chr(10).join(['• ' + f for f in results.get('analysis', {}).get('key_findings', [])])}

RECOMMENDATIONS:
{chr(10).join(['• ' + r for r in results.get('insights', {}).get('recommendations', [])])}

CITATIONS: {len(st.session_state.citations)}
Sources: {len(results.get('search_results', []))} web + {len(results.get('rag_results', []))} RAG
"""
        st.download_button(
            "📄 Text Summary",
            text_report,
            f"summary_{query[:20]}.txt",
            "text/plain"
        )
    
    with col3:
        # Citations export
        citations_text = "CITATIONS\n==========\n\n"
        for i, cite in enumerate(st.session_state.citations, 1):
            citations_text += f"{i}. {cite['source_title']}\n"
            citations_text += f"   URL: {cite['source_url']}\n"
            citations_text += f"   Agent: {cite['agent']}\n\n"
        
        st.download_button(
            "📑 Citations",
            citations_text,
            f"citations_{query[:20]}.txt",
            "text/plain"
        )

# Example queries
if not st.session_state.results:
    st.markdown("---")
    st.subheader("💡 Example Queries")
    
    examples = [
        "Analyze quantum computing breakthroughs and cybersecurity implications",
        "Impact of AI on healthcare diagnostics with ethical considerations",
        "Current state of renewable energy storage technology",
        "Gene editing advances and CRISPR ethical concerns",
        "Remote work effects on productivity and mental health",
        "Nuclear fusion energy recent developments"
    ]
    
    cols = st.columns(2)
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            if st.button(example, key=f"ex_{idx}", use_container_width=True):
                st.session_state.current_query = example
                st.rerun()

st.markdown("---")
st.caption("🚀 Advanced Multi-Agent Research System | Groq + Tavily + RAG + ChromaDB")