from fastapi import APIRouter
from pydantic import BaseModel
from utils.fetcher import fetch_url_content
from utils.parser import parse_html
from utils.summarizer import summarize_text

# Create router
router = APIRouter()

# Define request body schema
class URLRequest(BaseModel):
    url: str

# Define endpoint
@router.post("/summarize-url")
async def summarize_url(request: URLRequest):
    html = await fetch_url_content(request.url)
    text = parse_html(html)
    summary = await summarize_text(text[:1000])  # Limit to avoid OpenAI token limits
    return {"summary": summary}
