from fastapi import APIRouter
from backend.scraper import scrape_web 

router = APIRouter()

@router.get("/scrape")
async def scrape_endpoint(url: str):
    result = await scrape_web(url)
    return result
