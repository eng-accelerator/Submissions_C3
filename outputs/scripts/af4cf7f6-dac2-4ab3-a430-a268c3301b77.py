
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here is the corrected Playwright script with consistent indentation. This version uses 4 spaces for indentation throughout the code.
 
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
 
 ### Key Changes
 - The indentation level of all lines has been set to 4 spaces consistently.
 - The `await` statements are correctly aligned with the rest of the code within the `run` function.
   
 Now, this script should run without any `IndentationError`.

        await browser.close()


asyncio.run(run())
