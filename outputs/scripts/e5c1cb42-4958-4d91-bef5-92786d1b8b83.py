
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Sure! Here’s the corrected version of the original Playwright script with proper indentation:
 
 ```python
 import asyncio
 from playwright.async_api import async_playwright
 
 async def run():
     async with async_playwright() as p:
         browser = await p.chromium.launch(headless=False)
         page = await browser.new_page()
         
         await page.goto("https://www.google.com")  # Corrected indentation
         await page.fill("input[name='q']", "search query")
         await page.wait_for_selector("ul[role='listbox']")
         await page.keyboard.press("Enter")
         await page.wait_for_selector("#search")
         await page.wait_for_selector("div.g")
         
         await browser.close()
 
 asyncio.run(run())
 ```
 
 ### Key Adjustments:
 1. The `await page.goto("https://www.google.com")` line and subsequent lines are now correctly indented to be part of the `run` function.
 2. The indentation is consistent for all the lines inside the async context.
 
 This corrected script should now run without indentation errors.

        await browser.close()


asyncio.run(run())
