# Backend/utils/google_snapshot.py
from playwright.async_api import async_playwright
import base64
import asyncio

async def fetch_google_snapshot(query: str) -> dict[str, str]:
    """Fetch Google Search result snapshot and rendered HTML for a given query."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()

        url = f"https://www.google.com/search?q={query}"
        await page.goto(url, timeout=45000)
        await page.wait_for_timeout(2500)  # let results settle

        # Screenshot → base64 string
        screenshot_bytes = await page.screenshot(full_page=True)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

        # Rendered HTML (includes dynamically injected content)
        html = await page.content()

        await browser.close()

        return {
            "query": query,
            "snapshot": f"data:image/png;base64,{screenshot_b64}",
            "html": html
        }

# Test with:
# asyncio.run(fetch_google_snapshot("Elon Musk Twitter acquisition"))
