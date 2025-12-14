
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
