# backend/scaper.py
import asyncio
from typing import Dict
from playwright.async_api import async_playwright
import trafilatura
import httpx
from backend.utils.url_validator import is_valid_url

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

async def scrape_with_playwright(url: str) -> str:
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # headful برای جلوگیری از 403
            context = await browser.new_context(user_agent=HEADERS["User-Agent"])
            page = await context.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state('networkidle')
            content = await page.content()
            await browser.close()
            return content
    except Exception as e:
        return f"Playwright error: {str(e)}"

def scrape_with_trafilatura(url: str) -> str:
    
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            return text or ""
    except Exception as e:
        return f"Trafilatura error: {str(e)}"
    return ""

async def scrape_web(url: str) -> Dict[str, str]:
    
    if not is_valid_url(url):
        return {"success": False, "text": "", "error": "Invalid URL provided."}

    result_text = await scrape_with_playwright(url)
    if result_text.strip() and not result_text.startswith("Playwright error"):
        return {"success": True, "text": result_text, "error": ""}

   
    result_text = scrape_with_trafilatura(url)
    if result_text.strip() and not result_text.startswith("Trafilatura error"):
        return {"success": True, "text": result_text, "error": ""}

    return {"success": False, "text": "", "error": f"Failed to scrape content. Playwright: {result_text}"}

