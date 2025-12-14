import logging
import time
from playwright.sync_api import sync_playwright
import config

logger = logging.getLogger(__name__)

class AutoLoginAgent:
    """
    Agent designed to demonstrate automated authentication flows.
    """
    
    def execute_login(self, url, username, password):
        logger.info(f"AutoLogin Agent: Initiating sequence for {username}...")
        
        try:
            with sync_playwright() as p:
                # Launch browser for visual demo
                browser = p.chromium.launch(
                    headless=False, 
                    slow_mo=2000, # 2s delay for explanation
                    args=['--start-maximized']
                )
                context = browser.new_context(viewport={'width': 1280, 'height': 720})
                page = context.new_page()
                
                # 1. Navigate
                logger.info(f"Navigating to {url}...")
                page.goto(url)
                
                # 2. Identify Elements
                user_field = page.locator("#user-name")
                pass_field = page.locator("#password")
                login_btn = page.locator("#login-button")
                
                # Visual Highlight - Username
                user_field.evaluate("el => el.style.border = '4px solid #a855f7'") # Purple
                time.sleep(1)
                user_field.fill(username)
                
                # Visual Highlight - Password
                pass_field.evaluate("el => el.style.border = '4px solid #a855f7'")
                time.sleep(1)
                pass_field.fill(password)
                
                # 3. Action
                logger.info("Credentials entered. Attempting entry...")
                login_btn.evaluate("el => el.style.boxShadow = '0 0 20px #a855f7'")
                time.sleep(1)
                login_btn.click()
                
                # 4. Verification
                page.wait_for_url("**/inventory.html")
                success_marker = page.locator(".title")
                
                if success_marker.is_visible() and "Products" in success_marker.inner_text():
                    logger.info("Login Successful! Dashboard accessed.")
                    
                    # Celebration highlight
                    success_marker.evaluate("el => el.style.color = '#22c55e'") # Green text
                    success_marker.evaluate("el => el.innerText = '✅ ACCESS GRANTED'")
                    time.sleep(5) # Hold for applause
                    
                    return f"Login Sequence Complete: Access Granted to {username}."
                else:
                    return "Login Failed: Dashboard not found."

                browser.close()
                
        except Exception as e:
            logger.error(f"Login Agent Failed: {e}")
            raise e
