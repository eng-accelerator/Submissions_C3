def generate_base_playwright_script(steps):
    script = """
import asyncio
from playwright.async_api import async_playwright


async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()


"""
    for s in steps:
        script += f" {s}\n"


    script += """
        await browser.close()


asyncio.run(run())
"""


    return script