from fastapi import APIRouter
from backend.models import URLRequest
from backend.scraper import scrape_web
from backend.summarizer import summarize_text

router = APIRouter()

@router.post("/scrape-and-summarize")
async def scrape_and_summarize(req: URLRequest):  
    try:
        scraped = await scrape_web(req.url) 

        if not scraped.get("success"):
            return {
                "success": False,
                "message": "Failed to scrape the website.",
                "error": scraped.get("error", "Unknown scraping error")
            }

        article_text = scraped.get("text", "")
        if not article_text:
            return {
                "success": False,
                "message": "Scraped text is empty.",
                "error": "No content extracted from website"
            }

        summary_result = summarize_text(article_text)

        if not summary_result["success"]:
            return {
                "success": False,
                "message": "Summarization failed.",
                "error": summary_result.get("error", "Unknown summarization error")
            }

        return {
            "success": True,
            "original_text": article_text,
            "summary_text": summary_result["summary_text"]
        }

    except Exception as e:
        return {
            "success": False,
            "message": "Unexpected error occurred.",
            "error": str(e)
        }
