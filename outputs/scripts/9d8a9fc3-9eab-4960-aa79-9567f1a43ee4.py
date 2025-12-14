
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
