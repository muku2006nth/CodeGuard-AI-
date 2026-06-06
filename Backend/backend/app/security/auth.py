import os
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from dotenv import load_dotenv

load_dotenv()

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "super-secret-jwt-token-with-at-least-32-characters-long") # It's better to fetch this from Supabase Dashboard -> Settings -> API -> JWT Secret, but for local dev with Anon Key we can actually just verify with Supabase client or extract without full local verification if we trust the client library. Wait, we should use the Supabase python client to get the user from the token.

from supabase import create_client, Client

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

from dataclasses import dataclass

@dataclass
class UserContext:
    id: str
    token: str

async def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> UserContext:
    token = credentials.credentials
    try:
        user_response = supabase.auth.get_user(token)
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        return UserContext(id=user_response.user.id, token=token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
