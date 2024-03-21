import os
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import FastAPI, Depends, HTTPException,status
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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

class JWTBearer(HTTPBearer):
    def __init__(self, auto_erro: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_erro)

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,detail="Esquema de authenticação inválido",
                )
            return credentials.credentials
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não authenticado")

    def verify_token(self, token) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(token)
        except:
            payload
        if payload:
            isTokenValid = True
        return isTokenValid

jwt_bearer = JWTBearer()