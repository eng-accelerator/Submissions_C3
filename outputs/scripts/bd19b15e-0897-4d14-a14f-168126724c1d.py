
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Sure! Below is the corrected Playwright script with proper indentation:
 
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
 - Indented the `await page.fill(...)`, `await page.wait_for_selector(...)`, `await page.click(...)`, and `await page.wait_for_selector(...)` lines to be within the `run` function's block.
 
 This should resolve the indentation error, allowing the script to run properly.

        await browser.close()


asyncio.run(run())
