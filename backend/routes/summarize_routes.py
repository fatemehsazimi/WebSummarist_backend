from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.summarizer import summarize_text
from backend.models import TextRequest

router = APIRouter()

@router.post("/summarize")
async def summarize(req: TextRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Input text is empty.")
    result = summarize_text(req.text)
    return result