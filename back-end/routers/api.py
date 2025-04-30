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
from openai import AsyncOpenAI
from datetime import datetime



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

# Add this helper function for timestamps
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# --- Models ---
class URLRequest(BaseModel):
    url: str

class LoginRequest(BaseModel):
    password: str

class ChatRequest(BaseModel):
    url: str
    question: str
    chat_history: list[dict] = []  # List of previous messages

# --- Endpoints ---
@router.get("/")
async def root():
    return {"message": "API is alive"}

@router.post("/login")
async def login(request: LoginRequest):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 🔐 Login Attempt")
    
    if request.password == REAL_PASSWORD:
        token = secrets.token_hex(32)
        active_tokens.add(token)
        print(f"├── ✅ Login successful")
        print(f"└── Token generated: {token[:10]}...")
        return {"token": token}
    else:
        print(f"└── ❌ Login failed: Incorrect password")
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )

@router.post("/summarize-url")
@limiter.limit("10/minute")
async def summarize_url(request: Request, payload: URLRequest, authorization: str = Header(...)):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 🌐 New URL Summarization Request")
    print(f"├── Input URL: {payload.url}")
    
    token = authorization.replace("Bearer ", "")
    if token not in active_tokens:
        print(f"├── ❌ Authentication Failed: Invalid token")
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
        print(f"├── Processing URL: {raw_url}")
        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"http://{url}"
        print(f"├── Normalized URL: {url}")
        
        if validators.url(url) == True:
            print("├── 🔍 Fetching URL content...")
            html = await fetch_url_content(url)
            print("├── 📝 Parsing HTML...")
            text = parse_html(html)
            print(f"├── 📊 Extracted text length: {len(text)} characters")
            print("├── 🤖 Requesting OpenAI summary...")
            summary = await summarize_text(text[:5000])
            print(f"├── ✅ Summary generated: {len(summary)} characters")
            print(f"└── Summary preview: {summary[:100]}...")
            return {"summary": summary}
        else:
            print(f"└── ❌ Invalid URL format")
            return {"summary": "Invalid URL"}
    except Exception as e:
        print(f"└── ❌ Error: {str(e)}")
        return {"summary": f"Error processing URL: {str(e)}"}
    
    
    

@router.post("/logout")
async def logout(authorization: str = Header(...)):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 🚪 Logout Request")
    
    token = authorization.replace("Bearer ", "")
    active_tokens.discard(token)
    print(f"└── ✅ User logged out successfully")
    return {"message": "Logged out successfully"}

@router.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, payload: ChatRequest, authorization: str = Header(...)):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 💬 New Chat Request")
    print(f"├── Question: {payload.question}")
    print(f"├── URL Context: {payload.url if payload.url else 'None'}")
    print(f"├── Chat History Length: {len(payload.chat_history)} messages")
    
    token = authorization.replace("Bearer ", "")
    if token not in active_tokens:
        print(f"├── ❌ Authentication Failed: Invalid token")
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
        # Format chat history for context
        chat_context = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in payload.chat_history[-5:]
        ])
        print("├── 📜 Previous Messages:")
        for msg in payload.chat_history[-5:]:
            print(f"│   {msg['role']}: {msg['content'][:50]}...")
        
        # Get URL content if provided
        url_context = ""
        if payload.url:
            print("├── 🔍 Fetching URL content...")
            html = await fetch_url_content(payload.url)
            text = parse_html(html)
            url_context = f"\nURL Content Summary: {text[:2000]}..."
            print(f"├── 📊 URL context length: {len(url_context)} characters")
        
        # Prepare prompt for OpenAI
        prompt = f"""Context from URL: {url_context}

Previous conversation:
{chat_context}

User Question: {payload.question}

Please provide a helpful response based on the context and question."""

        print("├── 🤖 Sending request to OpenAI...")
        
        # Get response from OpenAI
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = await client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"├── ✅ Response received: {len(ai_response)} characters")
        print(f"└── Response preview: {ai_response[:100]}...")
        
        return {"response": ai_response}
        
    except Exception as e:
        print(f"└── ❌ Error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": f"Failed to process chat request: {str(e)}"
                }
            }
        )
