from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
import logging
from agents.navigator import NavigationAgent
from agents.extractor import ContentExtractionAgent
from agents.blog_generator import BlogGeneratorAgent
from agents.file_saver import FileSaverAgent
from agents.researcher import ResearchAgent
from agents.reviewer import ReviewerAgent
from agents.youtube import YouTubeAgent
import config

logger = logging.getLogger("Workflow")

class AgentState(TypedDict):
    mode: str # 'techcrunch' or 'research' or 'youtube'
    topic: Optional[str]
    url: Optional[str]
    html_content: Optional[str]
    article_data: Optional[dict]
    research_context: Optional[str]
    blog_content: Optional[str]
    final_content: Optional[str]
    output_files: Optional[list]
    error: Optional[str]
    logs: Optional[List[str]]
    # Auth fields
    username: Optional[str]
    password: Optional[str]

# ...

def sauce_node(state: AgentState):
    logger.info("--- [Node] Sauce Login ---")
    if state.get("error"): return {}
    
    try:
        agent = AutoLoginAgent()
        # Fallback to defaults to keep old behavior working if inputs missing
        url = state.get("url") or "https://www.saucedemo.com/"
        user = state.get("username") or "standard_user"
        pwd = state.get("password") or "secret_sauce"
        
        result = agent.execute_login(url, user, pwd)
        return {"final_content": result}
    except Exception as e:
        return {"error": str(e)}


def navigation_node(state: AgentState):
    logger.info("--- [Node] Navigation (TechCrunch) ---")
    nav = NavigationAgent()
    try:
        nav.start_browser()
        url = nav.find_ai_article()
        if not url: return {"error": "No AI article found."}
        nav.open_article(url)
        html = nav.get_page_content()
        nav.close()
        return {"url": url, "html_content": html}
    except Exception as e:
        if nav.browser: nav.close()
        return {"error": str(e)}

def extraction_node(state: AgentState):
    logger.info("--- [Node] Extraction ---")
    if state.get("error"): return {}
    try:
        extractor = ContentExtractionAgent()
        data = extractor.extract(state["html_content"])
        data['url'] = state.get('url')
        return {"article_data": data}
    except Exception as e:
        return {"error": str(e)}

def research_node(state: AgentState):
    logger.info(f"--- [Node] Research for: {state.get('topic')} ---")
    if state.get("error"): return {}
    try:
        researcher = ResearchAgent()
        context = researcher.research(state.get("topic"))
        return {"research_context": context}
    except Exception as e:
        return {"error": str(e)}

def generation_node(state: AgentState):
    logger.info("--- [Node] Blog Generation ---")
    if state.get("error"): return {}
    
    generator = BlogGeneratorAgent()
    
    # Decide source
    if state['mode'] == 'research':
        # Construct a pseudo-article dict from research
        data = {
            'headline': state.get('topic'),
            'body': state.get('research_context')
        }
    else:
        data = state.get('article_data')
    
    if not data: return {"error": "No data for generation."}

    try:
        content = generator.generate_blog(data)
        return {"blog_content": content}
    except Exception as e:
        return {"error": str(e)}

def review_node(state: AgentState):
    logger.info("--- [Node] Reviewer ---")
    if state.get("error"): return {}
    
    draft = state.get("blog_content")
    if not draft: return {"error": "No draft to review."}
    
    topic = state.get('topic') or state.get('article_data', {}).get('headline')
    
    try:
        reviewer = ReviewerAgent()
        polished = reviewer.review(draft, topic)
        return {"final_content": polished}
    except Exception as e:
         # Fallback to draft if review fails
        return {"final_content": draft, "error": f"Review failed: {e}"}

def youtube_node(state: AgentState):
    logger.info(f"--- [Node] YouTube Player ---")
    if state.get("error"): return {}
    
    query = state.get("topic")
    if not query: return {"error": "No query provided for YouTube."}
    
    try:
        player = YouTubeAgent()
        result_msg = player.play_video(query)
        # We misuse 'final_content' to pass the success message back to UI
        return {"final_content": result_msg}
    except Exception as e:
        return {"error": str(e)}

def saving_node(state: AgentState):
    logger.info("--- [Node] Saving ---")
    if state.get("error") and not state.get("final_content"): return {}
    
    content = state.get("final_content") or state.get("blog_content")
    
    # Determine Title
    if state['mode'] == 'research':
        title = state.get('topic')
    else:
        title = state.get('article_data', {}).get('headline', 'Untitled')
        
    saver = FileSaverAgent()
    try:
        files = []
        files.append(saver.save_as_txt(content, title))
        # Optional Docx
        docx = saver.save_as_docx(content, title)
        if docx: files.append(docx)
        return {"output_files": files}
    except Exception as e:
        return {"error": str(e)}

from agents.autologin import AutoLoginAgent

def sauce_node(state: AgentState):
    logger.info("--- [Node] Sauce Login ---")
    if state.get("error"): return {}
    
    try:
        agent = AutoLoginAgent()
        # Retrieve credentials from state (injected by server.py from UI request)
        url = state.get("url") or "https://www.saucedemo.com/"
        user = state.get("username") or "standard_user"
        pwd = state.get("password") or "secret_sauce"
        
        logger.info(f"Attempting login with user: {user}")
        result = agent.execute_login(url, user, pwd)
        return {"final_content": result}
    except Exception as e:
        return {"error": str(e)}

from agents.healer import DisasterRecoveryAgent

def healer_node(state: AgentState):
    logger.info("--- [Node] Self-Healing ---")
    error = state.get("error")
    if not error: return {}
    
    healer = DisasterRecoveryAgent()
    patch = healer.heal(error, state)
    
    if patch:
        # Log the intervention
        logs = state.get("logs", [])
        logs.append(f"⚠️ Error detected: {error[:50]}...")
        logs.append(f"🚑 Self-Correction: {patch.get('decision')}")
        patch['logs'] = logs
        return patch
    else:
        # Fatal error, pass it through
        return {"error": error}

def build_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("navigator", navigation_node)
    workflow.add_node("extractor", extraction_node)
    workflow.add_node("researcher", research_node)
    workflow.add_node("generator", generation_node)
    workflow.add_node("reviewer", review_node)
    workflow.add_node("youtube", youtube_node)
    workflow.add_node("saver", saving_node)
    workflow.add_node("healer", healer_node)
    workflow.add_node("sauce", sauce_node)
    
    # Conditional Entry
    def route_start(state):
        if state['mode'] == 'research':
            return "researcher"
        elif state['mode'] == 'youtube':
            return "youtube"
        elif state['mode'] == 'sauce':
             return "sauce"
        return "navigator"

    workflow.set_conditional_entry_point(
        route_start,
        {
            "researcher": "researcher", 
            "navigator": "navigator",
            "youtube": "youtube",
            "sauce": "sauce"
        }
    )
    
    # Smart Error Router
    def route_or_heal(state, next_node):
        if state.get("error"):
            return "healer"
        return next_node
        
    def route_after_heal(state):
        decision = state.get("decision")
        if decision == "reroute_research": return "researcher"
        if decision == "reroute_generation": return "generator"
        if decision == "retry": return state['mode'] # simplistic retry
        return END # Fatal
    
    # Edges with Error Interception
    workflow.add_conditional_edges("navigator", lambda s: route_or_heal(s, "extractor"), {"extractor": "extractor", "healer": "healer"})
    workflow.add_conditional_edges("extractor", lambda s: route_or_heal(s, "generator"), {"generator": "generator", "healer": "healer"})
    workflow.add_conditional_edges("researcher", lambda s: route_or_heal(s, "generator"), {"generator": "generator", "healer": "healer"})
    workflow.add_conditional_edges("generator", lambda s: route_or_heal(s, "reviewer"), {"reviewer": "reviewer", "healer": "healer"})
    workflow.add_conditional_edges("reviewer", lambda s: route_or_heal(s, "saver"), {"saver": "saver", "healer": "healer"})
    workflow.add_conditional_edges("youtube", lambda s: route_or_heal(s, END), {END: END, "healer": "healer"})
    workflow.add_conditional_edges("sauce", lambda s: route_or_heal(s, END), {END: END, "healer": "healer"})
    
    # Healer Logic
    workflow.add_conditional_edges(
        "healer",
        route_after_heal,
        {
            "researcher": "researcher",
            "generator": "generator",
            "techcrunch": "navigator",
            "youtube": "youtube",
            END: END
        }
    )
    
    workflow.add_edge("saver", END)
    
    return workflow.compile()
