from playwright.sync_api import sync_playwright
import time
import logging

logger = logging.getLogger(__name__)

class YouTubeAgent:
    def __init__(self):
        pass

    def play_video(self, query: str):
        """
        Searches for a video on YouTube and plays the first result.
        Uses persistent context to save login session/cookies.
        """
        logger.info(f"YouTube Agent: Searching for '{query}'...")
        
        user_data_dir = "user_data/chrome_profile"
        
        try:
            with sync_playwright() as p:
                # Use persistent context so user login/cookies are saved between sessions
                # This allows the user to log in once manually if they want, and it remembers.
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False, # We want to watch
                    slow_mo=2000,
                    viewport={'width': 1280, 'height': 720},
                    # permissions=['autoplay'] 
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate
                page.goto("https://www.youtube.com")
                
                # --- Handle Popups (Cookies / Login Nags) ---
                try:
                    # Generic consent buttons (adjust selectors based on region/ab tests)
                    # "Reject all" or "Accept all"
                    consent_button = page.locator('button[aria-label="Reject all"]').or_(
                                     page.locator('button[aria-label="Accept all"]')).first
                    if consent_button.is_visible(timeout=3000):
                        logger.info("Handling Cookie Consent...")
                        consent_button.click()
                except:
                    pass
                
                # --- Search ---
                # Try specific input name first, common on desktop
                search_input = page.locator('input[name="search_query"]').first
                
                # Fallback if the specific name isn't found (sometimes standard search box has different attributes)
                if not search_input.is_visible():
                     search_input = page.get_by_role("combobox", name="Search").first
                
                search_input.wait_for(state="visible", timeout=10000)
                search_input.click() # Focus
                search_input.fill(query)
                search_input.press("Enter")
                
                page.wait_for_load_state("networkidle")
                
                # Find first video result
                # ytd-video-renderer is the container, #video-title is the link title
                # We wait for the container first
                page.wait_for_selector('ytd-video-renderer', timeout=10000)
                
                video_locator = page.locator('ytd-video-renderer').first.locator('#video-title')
                
                if video_locator.is_visible():
                    # Visual flare
                    video_locator.scroll_into_view_if_needed()
                    # Ensure we don't crash if evaluate fails (detached element)
                    try:
                         video_locator.evaluate("el => el.style.border = '4px solid #ef4444'") # YouTube Red
                         video_locator.evaluate("el => el.style.boxShadow = '0 0 20px #ef4444'")
                    except:
                        pass
                    time.sleep(5) # Increased wait for demo explanation
                    
                    logger.info("Clicking video...")
                    video_locator.click()
                    
                    # Handle "Skip Ad" if we can? (Bonus)
                    # page.locator(".ytp-ad-skip-button").click() 
                    
                    # Wait for player to load
                    page.wait_for_selector('.html5-video-player')
                    
                    logger.info("Playing video... (Keeping browser open for 60 seconds)")
                    # Keep open for a minute so user can watch/listen
                    time.sleep(60)
                    
                else:
                    logger.warning("No video results found.")
                
                browser.close()
                logger.info("YouTube session ended.")
                return f"Played video for: {query}"
                
        except Exception as e:
            logger.error(f"YouTube Agent failed: {e}")
            return f"Error playing video: {str(e)}"
