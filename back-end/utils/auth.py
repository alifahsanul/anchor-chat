from fastapi import HTTPException
import secrets
import os
from datetime import datetime

# Store active tokens
active_tokens = set()

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def verify_token(token: str) -> bool:
    """Verify if the token is valid"""
    return token in active_tokens

def create_token() -> str:
    """Create a new authentication token"""
    token = secrets.token_hex(32)
    active_tokens.add(token)
    print(f"├── ✅ Login successful")
    print(f"└── Token generated: {token[:10]}...")
    return token

def remove_token(token: str) -> None:
    """Remove a token from active tokens"""
    active_tokens.discard(token)

def verify_password(password: str) -> bool:
    """Verify if the password is correct"""
    REAL_PASSWORD = os.getenv("ANCHORCHAT_PASSWORD")
    return password == REAL_PASSWORD 