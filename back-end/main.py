from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from routers.api import router as api_router
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from utils.limiter import limiter


load_dotenv()

# Initialize FastAPI app
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include the API router
app.include_router(api_router)

# Load secrets
CORRECT_PASSWORD = os.getenv("CORRECT_PASSWORD")
FAKE_TOKEN = os.getenv("FAKE_TOKEN")

# Get allowed origins from environment variable or use default
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://anchor-chat.vercel.app,https://anchor-chat-production.up.railway.app"
).split(",")

print("ALLOWED_ORIGINS", ALLOWED_ORIGINS)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # More secure CORS configuration
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    password: str

class ChatRequest(BaseModel):
    url: str
    question: str



