
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here’s the corrected Playwright script with consistent indentation using four spaces for each level of indentation:
 
 ```python
 import asyncio
 from playwright.async_api import async_playwright
 
 async def run():
     async with async_playwright() as p:
         browser = await p.chromium.launch(headless=False)
         page = await browser.new_page()
         
         await page.goto("https://www.google.com")
         await page.fill("input[name='q']", "search query")
         await page.wait_for_selector("div.suggestions")
         await page.keyboard.press("Enter")
         await page.wait_for_selector("#search")
         await page.wait_for_selector("div.g")
         
         await browser.close()
 
 asyncio.run(run())
 ```
 
 ### Key Changes Made:
 1. **Consistent Indentation:** All indentation is now done using four spaces.
 2. **Proper Nesting:** Each line is placed within the appropriate block, ensuring that all `await` statements are properly indented under the `run()` function.
 
 This should resolve the `IndentationError` you were encountering. Run this corrected script, and it should work without indentation issues.

        await browser.close()


asyncio.run(run())
