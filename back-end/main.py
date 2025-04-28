from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load secrets
CORRECT_PASSWORD = os.getenv("CORRECT_PASSWORD")
FAKE_TOKEN = os.getenv("FAKE_TOKEN")

class LoginRequest(BaseModel):
    password: str

class ChatRequest(BaseModel):
    url: str
    question: str

@app.get("/")
async def root():
    return {"message": "AnchorChat API is running"}

@app.post("/login")
async def login(request: LoginRequest):
    if request.password == CORRECT_PASSWORD:
        return {"token": FAKE_TOKEN}
    else:
        raise HTTPException(status_code=401, detail="Invalid password.")

@app.post("/chat")
async def chat(request: Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f"Bearer {FAKE_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    body = await request.json()
    url = body.get("url")
    question = body.get("question")

    return {"answer": f"Pretend I'm answering your question about {url}."}

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))  # Read from env, default to 8000
    uvicorn.run("main:app", host="0.0.0.0", port=port)
