
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here’s the corrected Playwright script with proper indentation:
 
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
 1. Fixed the indentation of the `await` statements within the `run()` function to ensure they are properly aligned with the function's block.
 2. Ensured consistent use of spaces (4 spaces used for indentation).
 
 Make sure to run the script in an environment where Playwright is installed, and the required browsers are set up (e.g., by running `playwright install`).

        await browser.close()


asyncio.run(run())
