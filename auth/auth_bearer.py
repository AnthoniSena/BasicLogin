import os
import jwt
from functools import wraps
from db.models import authentication_token
from db.session import Session
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException,status, Header
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable
from fastapi.requests import Request

ACCESS_TOKEN_EXPIRE_MINUTES=os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_MINUTES= os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES")
ALGORITHM=os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TOKEN_SECRET_KEY=os.getenv("JWT_ACCESS_TOKEN_SECRET_KEY")
JWT_REFRESH_TOKEN_SECRET_KEY =os.getenv("JWT_REFRESH_SECRET_KEY")

def decodeJWT(token: str):
    try:
        verified_token = jwt.decode(token, JWT_ACCESS_TOKEN_SECRET_KEY, ALGORITHM)
        return verified_token
    except InvalidTokenError:
        return None

def encodeJWT(token: str):
    pass

def token_required(func: Callable):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code=403, detail="Token de autenticação não fornecido.")
        
        
        return await func(request,*args, **kwargs)
        
    return wrapper
