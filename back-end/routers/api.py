from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi import Request
from utils.models import URLRequest, LoginRequest, ChatRequest
from utils.auth import verify_token, create_token, remove_token, verify_password, get_timestamp
from utils.chat_handler import process_chat_request
from utils.url_handler import process_url
from utils.limiter import limiter

# Create router
router = APIRouter()

@router.get("/")
async def root():
    return {"message": "API is alive"}

@router.post("/login")
async def login(request: LoginRequest):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 🔐 Login Attempt")
    
    if verify_password(request.password):
        token = create_token()
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
    if not verify_token(token):
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
        summary = await process_url(payload.url)
        return {"summary": summary}
    except Exception as e:
        print(f"└── ❌ Error: {str(e)}")
        return {"summary": f"Error processing URL: {str(e)}"}

@router.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, payload: ChatRequest, authorization: str = Header(...)):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 💬 New Chat Request")
    print(f"├── Question: {payload.question}")
    print(f"├── URL Context: {payload.url if payload.url else 'None'}")
    print(f"├── Chat History Length: {len(payload.chat_history)} messages")
    
    token = authorization.replace("Bearer ", "")
    if not verify_token(token):
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
        response = await process_chat_request(
            payload.question,
            payload.url,
            payload.chat_history
        )
        return {"response": response}
        
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

@router.post("/logout")
async def logout(authorization: str = Header(...)):
    timestamp = get_timestamp()
    print(f"\n[{timestamp}] 🚪 Logout Request")
    
    token = authorization.replace("Bearer ", "")
    remove_token(token)
    print(f"└── ✅ User logged out successfully")
    return {"message": "Logged out successfully"}
