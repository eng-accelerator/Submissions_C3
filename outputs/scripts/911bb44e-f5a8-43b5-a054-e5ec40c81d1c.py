
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here is the corrected Playwright script with proper indentation, ensuring that the indentation is consistent throughout the code:
 
 ```python
 import asyncio
 from playwright.async_api import async_playwright
 
 
 async def run():
     async with async_playwright() as p:
         browser = await p.chromium.launch(headless=False)
         page = await browser.new_page()
 
         await page.fill("input[type='search']", "search query")
         await page.wait_for_selector(".search-suggestions-dropdown")
         await page.click("button[type='submit']")
         await page.wait_for_selector(".search-results")
 
         await browser.close()
 
 
 asyncio.run(run())
 ```
 
 ### Changes Made:
 1. The indentation for all async operations (within the `run()` function) is consistently set to 4 spaces.
 2. Each code line under the `async with`, `page`, and `browser` blocks is indented correctly to match the Python standard for block indentation.
 
 ### Important Note:
 Make sure you have Playwright installed in your environment. You can set up Playwright and download the required browsers by running:
 
 ```bash
 pip install playwright
 playwright install
 ```
 
 This script now should run without any indentation issues. If you encounter other errors while executing the script, please provide the error message for further assistance.

        await browser.close()


asyncio.run(run())
