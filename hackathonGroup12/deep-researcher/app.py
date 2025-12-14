import streamlit as st
from clients import init_llm, init_tavily
from graph import build_graph
from errors import ConfigurationError
from logger import logger
from url_utils import remove_urls


st.set_page_config(
    page_title="🤖 AI Deep Researcher",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded")

st.title("🧠 Multi-Agent Deep Researcher")
st.write("A fully autonomous multi-hop multi-agent research pipeline.")

with st.sidebar:
    api_key = st.text_input("OpenRouter API Key",
        type="password",
        help="Get your API key from https://openrouter.ai/keys")
    
    tavily_api_key = st.text_input(
        "Tavily API Key",
        type="password",
        help="Get your API key from https://tavily.com"
    )
    youtube_api_key = st.text_input(
    "YouTube Data API Key",
    type="password",
    help="Enable YouTube research"
)

    
    if not all([api_key, tavily_api_key]):
        st.warning("Please enter your OpenRouter & Tavily API key to begin!")
        st.info("👆 Enter your API keys above and click 'Run Deep Research'")
        st.stop()
    
    st.success("✅ API Keys entered!")
    debug = st.toggle("Debug Mode")

try:
    if not all([api_key, tavily_api_key]):
        raise ConfigurationError

    llm = init_llm(api_key)
    tavily = init_tavily(tavily_api_key)
    # graph = build_graph(llm, tavily)
    graph = build_graph(
    llm,
    tavily,
    openrouter_key=api_key,
    youtube_key=youtube_api_key
)


except ConfigurationError:
    st.warning("🔑 Please enter your OpenRouter and Tavily API keys")
    st.stop()

except Exception as e:
    logger.exception("Initialization failed")
    st.error("🚨 Failed to initialize")
    if debug:
        st.exception(e)
    st.stop()

query = st.text_area(
    "Enter your research question:",
    placeholder="e.g., 'What are the emerging trends in AI agentic architectures?'",
    height=150
)

if st.button("🚀 Run Deep Research", type="primary"):
    if not query.strip() and remove_urls(query.strip()):
        st.error("Please enter a query.")
        st.stop()

    st.subheader("Pipeline Execution")
    st.info("Running multi-agent reasoning pipeline…")
    state = {"query": query}

    # Expanders for displaying each step
    ui = {
        "youtube": st.expander("▶️ YouTube Agent", False),
    "retriever": st.expander("🔎 Retriever Agent", False),
        "structurer": st.expander("📘 Structurer Agent", False),
        "analysis": st.expander("🧩 Analysis Agent", False),
        "factcheck": st.expander("✔️ Fact-Checking Agent", False),
        "expert": st.expander("👨‍🏫 Expert Interpretation", False),
        "critique": st.expander("🛡️ Red-Team Critique", False),
        "insights": st.expander("💡 Insight Generation", False),
        "report": st.expander("📄 Final Report", True)
    }
    final_report_text = None

    try:
        with st.spinner("Processing..."):
            for event in graph.stream(state, stream_mode="updates"):
                for node, data in event.items():
                    key = list(data.keys())[-1]
                    ui[node].write(data[key])
                    if node == "report":
                        final_report_text = data[key]

        st.success("✔️ Research Complete")

        if final_report_text:
            from pdf_utils import generate_pdf_from_text

            pdf_buffer = generate_pdf_from_text(
                title="AI Deep Research Report",
                content=final_report_text
            )

            st.download_button(
                label="📄 Download Final Report as PDF",
                data=pdf_buffer,
                file_name="deep_research_report.pdf",
                mime="application/pdf"
                )

    except Exception as e:
        logger.exception("Pipeline error")
        st.error("❌ Research failed")
        if debug:
            st.exception(e)
