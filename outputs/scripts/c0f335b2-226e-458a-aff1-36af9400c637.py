
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here’s a corrected version of the Playwright script, ensuring that the indentation is consistent and appropriate throughout:
 
 ```python
 import asyncio
 from playwright.async_api import async_playwright
 
 async def run():
     async with async_playwright() as p:
         browser = await p.chromium.launch(headless=False)
         page = await browser.new_page()
 
         await page.goto("https://www.google.com")
         await page.fill("input[name='q']", "search query")
         await page.wait_for_selector("ul[role='listbox']")
         await page.keyboard.press("Enter")
         await page.wait_for_selector("#search")
         await page.wait_for_selector("div.g")
 
         await browser.close()
 
 # Run the async function
 asyncio.run(run())
 ```
 
 ### Key Adjustments:
 1. Consistent indentation of 4 spaces is maintained throughout the script.
 2. Each line under the `async def run()` function is correctly indented to indicate it's part of the function.
 
 ### Steps to Ensure Indentation is Correct:
 1. **Single Style**: Use spaces for indentation, as recommended by PEP 8; do not mix spaces and tabs.
 2. **Block Structure**: Ensure that the indentation reflects the block structure of the code accurately.
 
 This script should now run without any indentation errors.

        await browser.close()


asyncio.run(run())
