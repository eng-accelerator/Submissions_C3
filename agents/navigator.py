import time
from playwright.sync_api import sync_playwright, Page
import config
import logging

logger = logging.getLogger(__name__)

class NavigationAgent:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start_browser(self):
        """Starts the browser session."""
        try:
            logger.info("Starting browser...")
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=config.HEADLESS_MODE,
                slow_mo=2000  # Add 2 second delay between actions for visibility
            )
            self.page = self.browser.new_page()
            logger.info("Browser started successfully.")
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    def find_ai_article(self) -> str:
        """
        Navigates to TechCrunch, looks for an AI article, and returns its URL.
        """
        if not self.page:
            raise Exception("Browser not started. Call start_browser() first.")

        try:
            logger.info(f"Navigating to {config.TECHCRUNCH_URL}...")
            self.page.goto(config.TECHCRUNCH_URL, timeout=config.BROWSER_TIMEOUT)
            
            # Wait for content to load
            self.page.wait_for_load_state("domcontentloaded")
            
            # Scroll down to load more dynamic content
            self.page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(1)

            logger.info("Scanning for AI articles...")
            
            article_links = self.page.query_selector_all('a[href*="/20"]') # TechCrunch articles usually have date in URL
            
            candidates = []
            
            for link in article_links:
                text = link.inner_text()
                href = link.get_attribute('href')
                
                # Basic check if it looks like an AI article
                if "AI" in text or "Artificial Intelligence" in text or "GenAI" in text:
                    candidates.append((link, href, text))

            target_url = None
            
            if candidates:
                # Random Selection
                import random
                selected_link, target_url, text = random.choice(candidates)
                logger.info(f"Randomly selected AI article from {len(candidates)} candidates: {text} -> {target_url}")
                
                # Visual Highlight
                if config.HEADLESS_MODE is False:
                     selected_link.scroll_into_view_if_needed()
                     try:
                        selected_link.evaluate("el => el.style.border = '5px solid red'")
                        selected_link.evaluate("el => el.style.boxShadow = '0 0 20px red'")
                     except: pass
                     self.page.wait_for_timeout(5000) # Wait 5s to show selection for demoExplanation

            # Fallback: Navigate to AI category if no specific article found on home page
            if not target_url:
                logger.info("No explicit AI article found on homepage. Checking AI category.")
                self.page.goto(f"{config.TECHCRUNCH_URL}/category/artificial-intelligence/", timeout=config.BROWSER_TIMEOUT)
                self.page.wait_for_load_state("domcontentloaded")
                
                # Scroll a bit
                self.page.evaluate("window.scrollTo(0, 500)")
                time.sleep(1)
                
                # On the AI category page, almost any article link is valid.
                self.page.wait_for_selector('a[href*="/20"]') 
                cat_links = self.page.query_selector_all('a[href*="/20"]')
                
                # Filter out very short texts (often just images or metadata links) to be safe
                valid_links = [l for l in cat_links if len(l.inner_text()) > 10]
                
                if valid_links:
                    import random
                    selected_link = random.choice(valid_links)
                    target_url = selected_link.get_attribute('href')
                    logger.info(f"Randomly selected article from AI category: {target_url}")
                    
                    if config.HEADLESS_MODE is False:
                        selected_link.scroll_into_view_if_needed()
                        try:
                           selected_link.evaluate("el => el.style.border = '5px solid red'")
                        except: pass
                        self.page.wait_for_timeout(2000)
                else:
                    # Absolute fallback to first one if random logic fails
                     target_url = self.page.eval_on_selector('a[href*="/20"]', 'el => el.href')

            return target_url

        except Exception as e:
            logger.error(f"Error during navigation: {e}")
            raise

    def open_article(self, url: str):
        """Navigates to a specific article URL."""
        logger.info(f"Opening article: {url}")
        self.page.goto(url, timeout=config.BROWSER_TIMEOUT)
        self.page.wait_for_load_state("domcontentloaded")

    def get_page_content(self):
        """Returns the HTML content of the current page."""
        return self.page.content()

    def close(self):
        """Clean up resources."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        logger.info("Browser closed.")
