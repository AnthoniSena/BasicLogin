from repository.auth_bearer_repository import AuthBearerRepository
from fastapi import Request, HTTPException, status
from utils.utils import decode
import os

ALGORITHM=os.getenv("JWT_ALGORITHM")
HTTP_ACCESS_TOKEN_SECRET_KEY=os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")

class AuthBearerService:
    def __init__(self) -> None:
        self.auth_bearer_repository = AuthBearerRepository()

    async def validate_token(self, request: Request):
        bearer_token = request.headers.get("Authorization")

        if bearer_token == None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de autenticação não fornecido.")
        
        token_value = bearer_token.split(" ")[1]

        decoded_token = decode(token_value, HTTP_ACCESS_TOKEN_SECRET_KEY, ALGORITHM)

        valid_token = await self.auth_bearer_repository.validate_token(token=decoded_token["token"])

        if decoded_token == None or not valid_token:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação inválido")
        
        if valid_token:
            return True
        return False
