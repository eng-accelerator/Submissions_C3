
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here’s a corrected and properly formatted Playwright script that uses consistent indentation (4 spaces) and addresses any previous issues. This script utilizes the async Playwright API to automate a simple task in a headless Chromium browser:
 
 ```python
 import asyncio
 from playwright.async_api import async_playwright
 
 async def run():
     async with async_playwright() as p:
         # Launch a Chromium browser
         browser = await p.chromium.launch(headless=False)
         
         # Create a new page
         page = await browser.new_page()
 
         # Navigate to Google
         await page.goto("https://www.google.com")
         
         # Fill in the search box with the query
         await page.fill("input[name='q']", "search query")
         
         # Wait for suggestions to show up and press Enter
         await page.wait_for_selector("ul[role='listbox']")
         await page.keyboard.press("Enter")
         
         # Wait for the search results to load
         await page.wait_for_selector("#search")
         await page.wait_for_selector("div.g")
 
         # Close the browser
         await browser.close()
 
 # Run the async function
 asyncio.run(run())
 ```
 
 ### Key Points:
 1. **Consistent Indentation**: The script uses 4 spaces for each indentation level, which is standard in Python.
 2. **Sequential Structure**: Each step of the script follows logically from launching the browser to performing actions on the page and finally closing the browser.
 3. **Comments for Clarity**: Inline comments have been added to explain significant steps in the automation process.
 
 ### Functionality:
 - The script opens a Chromium browser (non-headless for visibility).
 - It navigates to Google's homepage, fills in the search input, waits for suggestions, presses Enter, and finally waits for search results to display before closing the browser.
 
 Make sure you have the Playwright library installed in your environment in order to run this script successfully. You can install it via pip:
 
 ```bash
 pip install playwright
 ```
 Then, run the following command to install the necessary browser binaries:
 
 ```bash
 playwright install
 ```

        await browser.close()


asyncio.run(run())
