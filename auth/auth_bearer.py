import os
import jwt
from functools import wraps
from db.models import authentication_token
from db.session import Session
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException,status, Header
from fastapi import Request, HTTPException
from typing import Callable
from db.session import Session
from fastapi.requests import Request
from controllers.authentication_token_controller import AuthenticationTokenController

ALGORITHM=os.getenv("JWT_ALGORITHM")
HTTP_ACCESS_TOKEN_SECRET_KEY=os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")

def decode_access_token(token: str):
    try:
        decoded_acces_token = jwt.decode(token, HTTP_ACCESS_TOKEN_SECRET_KEY, ALGORITHM)
        return decoded_acces_token
    except InvalidTokenError:
        return None

def encodeJWT(token: str):
    pass

def token_required(func: Callable):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        authentication_token = AuthenticationTokenController(SessionLocal=Session)
        bearer_token = request.headers.get("Authorization")
        if not bearer_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de autenticação não fornecido.")
        token = bearer_token.split(" ")[1]
        decoded_token = decode_access_token(token)
        print(authentication_token.validate_token(decoded_token))
        if decoded_token == None or not authentication_token.validate_token(decoded_token):
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação inválido")
        
        return await func(request,*args, **kwargs)
        
    return wrapper
