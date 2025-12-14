
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here is a corrected version of the Playwright script with consistent indentation:
 
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
 
 ### Key Points:
 
 - The function `run` has a consistent indentation level, using 4 spaces for each level of indentation.
 - All asynchronous operations related to the page are indented properly within the `run` function block.
 - The script includes the required `asyncio.run(run())` call to execute the asynchronous `run` function.
 
 This structure should eliminate any indentation errors and allow the script to run as expected.

        await browser.close()


asyncio.run(run())
