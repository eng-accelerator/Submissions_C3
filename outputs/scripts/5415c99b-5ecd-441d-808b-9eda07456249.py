
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


 Here's a corrected and cleanly formatted Playwright script using the async API, ensuring consistent indentation and a clear structure:
 
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
         
         # Optionally, print the title of the first result for verification
         title = await page.title()
         print(f"Page Title: {title}")
         
         # Close the browser
         await browser.close()
 
 # Run the async function
 if __name__ == "__main__":
     asyncio.run(run())
 ```
 
 ### Key Features:
 1. **Consistent Indentation**: The script uses 4 spaces for indentation throughout, aligning with Python's PEP 8 style guide.
 2. **Logical Progression**: Each step of the automation process follows a clear and logical order—from launching the browser to printing the page title.
 3. **Search Functionality**: The script performs a Google search based on a query and handles the entire flow from inputting the search term to displaying results.
 
 ### Setup Instructions:
 To run this script successfully, follow these steps:
 
 1. **Install Playwright**:
    ```bash
    pip install playwright
    ```
 
 2. **Install browser binaries**:
    ```bash
    playwright install
    ```
 
 3. **Run the script**:
    - Save the script in a file, for example, `script.py`.
    - Run it using:
    ```bash
    python script.py
    ```
 
 ### Additional Notes:
 - Running with `headless=False` allows you to see the browser actions in real time. Change it to `headless=True` if you want it to run without a GUI.
 - Customize the search query in the `await page.fill("input[name='q']", "search query")` line to search for different terms of your choice.

        await browser.close()


asyncio.run(run())
