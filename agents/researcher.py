from tavily import TavilyClient
from playwright.sync_api import sync_playwright
import config
import logging
import time

logger = logging.getLogger(__name__)

class ResearchAgent:
    def __init__(self):
        self.api_key = config.TAVILY_API_KEY
        self.client = None
        if self.api_key:
            self.client = TavilyClient(api_key=self.api_key)
        else:
            logger.warning("TAVILY_API_KEY not found. Research will be simulated.")

    def _visual_search_demo(self, topic: str):
        """
        Visually demonstrates the research process using Playwright.
        This provides the 'live action' feel the user requested.
        """
        if config.HEADLESS_MODE: 
            return

        try:
            logger.info("Executing visual search demo...")
            with sync_playwright() as p:
                # Launch with slow_mo for visibility
                browser = p.chromium.launch(headless=False, slow_mo=2000)
                page = browser.new_page()
                
                # Go to a visual search engine (DuckDuckGo is cleaner for automation)
                page.goto("https://duckduckgo.com")
                
                # Type the topic visualy
                search_box = page.locator('input[name="q"]')
                search_box.fill(topic)
                
                # Press enter
                search_box.press("Enter")
                page.wait_for_load_state("networkidle")
                
                # Scroll a bit to simulate reading
                page.evaluate("window.scrollTo(0, 400)")
                time.sleep(1)
                page.evaluate("window.scrollTo(0, 800)")
                
                # Highlight the top result to show 'selection'
                first_result = page.locator('article, .react-results--main li').first
                if first_result.count() > 0:
                     first_result.scroll_into_view_if_needed()
                     first_result.evaluate("el => el.style.border = '4px solid #6366f1'") # Agent color
                     time.sleep(5) # Increased wait for demo explanation

                browser.close()
                logger.info("Visual demo complete.")
        except Exception as e:
            logger.warning(f"Visual demo failed (non-critical): {e}")

    def research(self, topic: str) -> str:
        """
        Performs web search on the topic and returns a summary of findings.
        """
        # Trigger the visual enactment first
        self._visual_search_demo(topic)

        if not self.client:
            return f"Simulated research results for: {topic}\n\n[Tavily Key Missing - Please Add to .env]\n\nFact 1: {topic} is interesting.\nFact 2: More data needed."
        
        try:
            logger.info(f"Researching topic: {topic}...")
            # Using basic search for MVP, getting comprehensive context
            response = self.client.search(
                query=f"latest news and deep analysis on {topic}",
                search_depth="advanced",
                max_results=5,
                include_answer=True
            )
            
            # extract answer and context
            answer = response.get('answer', '')
            results = response.get('results', [])
            
            context_str = f"Overview:\n{answer}\n\nDetailed Findings:\n"
            for res in results:
                context_str += f"- {res['title']}: {res['content']}\n"
                
            logger.info("Research complete.")
            return context_str
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return f"Error during research: {str(e)}"
