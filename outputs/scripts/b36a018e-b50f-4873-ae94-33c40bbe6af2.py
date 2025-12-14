
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here's a corrected version of the Playwright script with proper indentation, ensuring that everything is clear and organized:
 
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
 
 ### Key Adjustments Ensured:
 1. **Consistent Indentation**: Every line under the `async def run()` function is indented with exactly 4 spaces, maintaining consistency.
 2. **Proper Structure**: The indentation clearly defines the blocks of code that belong together, improving readability.
 
 ### Additional Tips for Avoiding Indentation Errors:
 - **Use a Code Editor**: A good code editor will highlight indentation issues and can auto-format your code to ensure consistency.
 - **Check Settings**: Ensure your text editor is set to use spaces, not tabs, for indentation. This is often configurable.
 - **Visualize Indents**: Some editors allow you to visualize whitespace characters, which can help in identifying mixed spaces and tabs.
 
 This code should run correctly and perform a simple search on Google, filling the search box, submitting the form, and waiting for results.

        await browser.close()


asyncio.run(run())
