import streamlit as st
from config import Config
from utils.logging import logger

st.set_page_config(page_title="Multi-Agent Deep Researcher", page_icon="🕵️‍♂️", layout="wide")

def render_sidebar():
    st.sidebar.header("⚙️ Configuration")
    
    # API Keys
    with st.sidebar.expander("API Keys", expanded=True):
        st.session_state['openai_api_key'] = st.text_input("OpenAI API Key", type="password")
        st.session_state['serper_api_key'] = st.text_input("Google Serper API Key", type="password", help="Get free key at serper.dev")
        st.session_state['tavily_api_key'] = st.text_input("Tavily API Key", type="password")
        st.session_state['anthropic_api_key'] = st.text_input("Anthropic API Key", type="password")
        st.session_state['gemini_api_key'] = st.text_input("Gemini API Key", type="password")
    
    # Research Discipline
    st.sidebar.header("📚 Research Discipline")
    discipline = st.sidebar.selectbox(
        "Select Discipline",
        ["Scientific & Academic Research", "Business & Market Analysis", "Finance & Law", "IT Technology & AI Development"]
    )
    return discipline

def main():
    st.title("🕵️‍♂️ Multi-Agent Deep Researcher")
    st.markdown("### Deep, multi-hop, multi-modal research with iterative reasoning.")
    
    discipline = render_sidebar()
    
    # Key Validation Status
    keys_status = Config.validate_keys()
    if not any(keys_status.values()):
        st.warning("⚠️ No API keys provided. Running in limited fallback mode (Open Source only).")
    else:
        active_keys = [k for k, v in keys_status.items() if v]
        st.success(f"✅ Active Agents: {', '.join(active_keys).upper()}")

    # Input Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        query = st.text_area("Research Query", height=150, placeholder="Enter your complex research question here...")
    
    with col2:
        st.markdown("#### Additional Context")
        uploaded_files = st.file_uploader("Upload Notes/Docs (PDF, DOCX)", accept_multiple_files=True)
        doi_input = st.text_input("DOI or arXiv ID (Optional)", placeholder="e.g., 10.1234/example or 2301.12345")
        img_video_url = st.text_input("Image/Video URL (Optional)")

    if st.button("🚀 Start Deep Research", type="primary"):
        if not query:
            st.error("Please enter a research query.")
        else:
            st.info(f"Starting research on: **{query}**")
            
            # Initialize Session State for results if not present
            if "research_results" not in st.session_state:
                st.session_state.research_results = None

            with st.spinner("🤖 Agents are working... (This may take 1-2 minutes)"):
                # Prepare State
                from graph.workflow import app_graph
                from modules.document_processor import DocumentProcessor
                
                processed_files = []
                if uploaded_files:
                    processed_files = DocumentProcessor.process_uploaded_files(uploaded_files)
                
                # Process DOI/arXiv if provided
                if doi_input:
                    # Add DOI to query or process separately
                    from tools.search_tools import SearchTools
                    search_tools = SearchTools()
                    if search_tools.is_doi(doi_input) or search_tools.is_arxiv_id(doi_input):
                        # Resolve DOI/arXiv and add to query context
                        doi_results = search_tools.search(doi_input, include_academic=True)
                        if doi_results:
                            # Add as a special reference document
                            for result in doi_results:
                                processed_files.append({
                                    "source": f"Reference: {result.get('source', 'DOI/arXiv')}",
                                    "content": result.get("content", ""),
                                    "type": "reference",
                                    "url": result.get("url", "")
                                })
                
                initial_state = {
                    "task": query,
                    "discipline": discipline,
                    "uploaded_files": processed_files if processed_files else [],
                    "iteration_count": 0,
                    "findings": []
                }
                
                # Execute Graph
                try:
                    final_state = app_graph.invoke(initial_state)
                    st.session_state.research_results = final_state
                    st.success("Research Complete!")
                except Exception as e:
                    st.error(f"An error occurred during execution: {e}")
                    import traceback
                    error_trace = traceback.format_exc()
                    st.code(error_trace)
                    logger.error(f"Graph execution error: {error_trace}")

    # Display Results
    if st.session_state.get("research_results"):
        results = st.session_state.research_results
        
        # Tabs for organized view
        tab1, tab2, tab3, tab4 = st.tabs(["📄 Executive Summary & Report", "📊 Insights & Sources", "🔄 Execution Trace", "💾 Download"])
        
        with tab1:
            st.markdown(results.get("final_report", "No report generated."))
        
        with tab2:
            st.subheader("Hypotheses Generated")
            hypotheses = results.get("hypotheses", [])
            if hypotheses:
                for i, hypothesis in enumerate(hypotheses, 1):
                    st.success(f"**Hypothesis {i}:** {hypothesis}")
            else:
                st.write("No hypotheses generated.")
            
            st.subheader("Key Insights")
            for insight in results.get("insights", []):
                st.info(insight)
            
            st.subheader("Implications")
            implications = results.get("implications", [])
            if implications:
                for implication in implications:
                    st.warning(implication)
            else:
                st.write("No implications identified.")
            
            st.subheader("Research Questions")
            research_questions = results.get("research_questions", [])
            if research_questions:
                for q in research_questions:
                    st.write(f"❓ {q}")
            else:
                st.write("No research questions generated.")
                
            st.subheader("Source Credibility")
            sources = results.get("sources", [])
            if sources:
                st.dataframe(sources)
            else:
                st.write("No sources scored.")

        with tab3:
            st.json(results.get("plan", {}))
            st.markdown("### Iteration Count")
            st.write(results.get("iteration_count", 0))

        with tab4:
            from modules.report_generator import ReportGenerator
            report_content = results.get("final_report", "")
            if report_content:
                pdf_bytes = ReportGenerator.generate_pdf_report(report_content)
                st.download_button(
                    label="Download PDF Report",
                    data=pdf_bytes,
                    file_name="Deep_Research_Report.pdf",
                    mime="application/pdf"
                )
                st.download_button(
                    label="Download Markdown",
                    data=report_content,
                    file_name="Deep_Research_Report.md",
                    mime="text/markdown"
                )

if __name__ == "__main__":
    main()

