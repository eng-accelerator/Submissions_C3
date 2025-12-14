import os
import sys
import logging
from typing import TypedDict, Optional
from dotenv import load_dotenv

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph.graph import StateGraph, END

# Import existing agent logic
from agents.navigator import NavigationAgent
from agents.extractor import ContentExtractionAgent
from agents.blog_generator import BlogGeneratorAgent
from agents.file_saver import FileSaverAgent
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LangGraph-Main")

# Define Flow State
class AgentState(TypedDict):
    url: Optional[str]
    html_content: Optional[str]
    article_data: Optional[dict]
    blog_content: Optional[str]
    output_files: Optional[list]
    error: Optional[str]

# --- Nodes ---

def navigation_node(state: AgentState):
    """
    Node responsible for searching and retrieving article HTML.
    Functionally combines finding and loading the page to keep browser session contained.
    """
    logger.info("--- [Node] Navigation ---")
    nav = NavigationAgent()
    try:
        nav.start_browser()
        url = nav.find_ai_article()
        
        if not url:
            return {"error": "No AI article found."}
        
        nav.open_article(url)
        html = nav.get_page_content()
        nav.close()
        
        return {"url": url, "html_content": html}
        
    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        if nav.browser:
            nav.close()
        return {"error": str(e)}

def extraction_node(state: AgentState):
    """
    Node responsible for parsing the HTML into structured data.
    """
    logger.info("--- [Node] Extraction ---")
    if state.get("error"):
        return {} # Pass through error
        
    html = state.get("html_content")
    if not html:
        return {"error": "No HTML content to extract."}
        
    extractor = ContentExtractionAgent()
    try:
        data = extractor.extract(html)
        # Add URL to data if needed by generator
        data['url'] = state.get('url')
        return {"article_data": data}
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return {"error": str(e)}

def blog_generation_node(state: AgentState):
    """
    Node responsible for generating the blog post using LLM.
    """
    logger.info("--- [Node] Blog Generation ---")
    if state.get("error"):
        return {}

    data = state.get("article_data")
    if not data:
        return {"error": "No article data available."}

    # Check for API key presence
    if not config.OPENAI_API_KEY and not config.OPENROUTER_API_KEY:
        logger.warning("API Key missing. Returning raw body as blog.")
        return {"blog_content": f"Title: {data.get('headline')}\n\n[API Key Missing]\n\n{data.get('body')}"}

    generator = BlogGeneratorAgent()
    try:
        blog_post = generator.generate_blog(data)
        return {"blog_content": blog_post}
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        return {"error": str(e)}

def file_saving_node(state: AgentState):
    """
    Node responsible for saving the generated content to files.
    """
    logger.info("--- [Node] File Saving ---")
    if state.get("error"):
        logger.error(f"Skipping save due to previous error: {state['error']}")
        return {}

    content = state.get("blog_content")
    data = state.get("article_data")
    title = data.get("headline", "Untitled") if data else "Untitled"
    
    if not content:
        return {"error": "No content to save."}
        
    saver = FileSaverAgent()
    saved_files = []
    
    try:
        txt_path = saver.save_as_txt(content, title)
        saved_files.append(txt_path)
        
        docx_path = saver.save_as_docx(content, title)
        if docx_path:
            saved_files.append(docx_path)
            
        logger.info(f"Files saved: {saved_files}")
        return {"output_files": saved_files}
    except Exception as e:
        logger.error(f"Saving failed: {e}")
        return {"error": str(e)}

# --- Graph Construction ---

def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("navigator", navigation_node)
    graph.add_node("extractor", extraction_node)
    graph.add_node("generator", blog_generation_node)
    graph.add_node("saver", file_saving_node)
    
    graph.set_entry_point("navigator")
    
    graph.add_edge("navigator", "extractor")
    graph.add_edge("extractor", "generator")
    graph.add_edge("generator", "saver")
    graph.add_edge("saver", END)
    
    return graph.compile()

def main():
    load_dotenv()
    logger.info("Starting LangGraph Agent...")
    
    app = build_graph()
    
    # Run the graph
    inputs = {"url": None, "html_content": None, "article_data": None}
    
    # invokation
    result = app.invoke(inputs)
    
    if result.get("error"):
        logger.error(f"Workflow finished with error: {result['error']}")
    else:
        logger.info("Workflow finished successfully!")
        logger.info(f"Output files: {result.get('output_files')}")

if __name__ == "__main__":
    main()
