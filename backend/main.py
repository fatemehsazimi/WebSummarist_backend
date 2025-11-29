from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.scrape_routes import router as scrape_router
from backend.routes.summarize_routes import router as summarize_router
from backend.routes.scrape_summarize_routes import router as scrape_summarize_router

from backend.exceptions import add_exception_handlers

app = FastAPI(title="Web Summarizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_exception_handlers(app)

app.include_router(scrape_router, prefix="/api", tags=["scraper"])
app.include_router(summarize_router, prefix="/api", tags=["summarize"])
app.include_router(scrape_summarize_router, prefix="/api", tags=["scrape_and_summarize"])

@app.get("/")
def root():
    return {"message": "API is running"}
