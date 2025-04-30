from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from utils.fetcher import fetch_url_content
from utils.parser import parse_html
from utils.summarizer import summarize_text
import secrets
import os
from dotenv import load_dotenv
from fastapi import Request
from utils.limiter import limiter
import validators



# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Create router
router = APIRouter()

# In-memory store for active session tokens
active_tokens = set()

# Load real password from .env
REAL_PASSWORD = os.getenv("ANCHORCHAT_PASSWORD")
if REAL_PASSWORD is None:
    raise Exception("ANCHORCHAT_PASSWORD not found in environment variables!")

# --- Models ---
class URLRequest(BaseModel):
    url: str

class LoginRequest(BaseModel):
    password: str

# --- Endpoints ---
@router.get("/")
async def root():
    return {"message": "API is alive"}

@router.post("/login")
async def login(request: LoginRequest):
    if request.password == REAL_PASSWORD:
        token = secrets.token_hex(32)  # Generate a secure random token
        active_tokens.add(token)       # Save it as active
        return {"token": token}
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

@router.post("/summarize-url")
@limiter.limit("10/minute")
async def summarize_url(request: Request, payload: URLRequest, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    if token not in active_tokens:
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": 401,
                    "message": "Unauthorized access. Please login again."
                }
            }
        )
    try:
        raw_url = payload.url
        print('raw_url:', raw_url)
        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        print('url:', url)
        if validators.url(url) == True:
            html = await fetch_url_content(url)
            text = parse_html(html)
            summary = await summarize_text(text[:5000])  # Limit input length
            return {"summary": summary}
        else:
            return {"summary": "Invalid URL"}
    except Exception as e:
        print(f"Error: {e}")
        return {"summary": "Invalid URL"}
    
    
    

@router.post("/logout")
async def logout(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    active_tokens.discard(token)  # Remove token if exists
    return {"message": "Logged out successfully"}
