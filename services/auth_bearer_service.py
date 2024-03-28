from repository.auth_bearer_repository import AuthBearerRepository
from fastapi import Request, HTTPException, status
from utils.utils import decode
import os

ALGORITHM=os.getenv("JWT_ALGORITHM")
HTTP_ACCESS_TOKEN_SECRET_KEY=os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")
JWT_ACCESS_TOKEN_SECRET_KEY=os.getenv("JWT_ACCESS_TOKEN_SECRET_KEY")

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

    async def validate_specific_user_token(self, request: Request, kwargs: dict):
        if 'form_data' in kwargs:
            user_id = dict(kwargs["form_data"])["user_id"]
        elif 'user_id' in kwargs:
            user_id = kwargs
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Id de usuário não fornecido.")

        coded_token = request.headers.get("Authorization").split(" ")[1]

        token = decode(coded_token, HTTP_ACCESS_TOKEN_SECRET_KEY, ALGORITHM)

        token = str(token["token"])

        token_info = decode(token, JWT_ACCESS_TOKEN_SECRET_KEY, ALGORITHM)

        if user_id == token_info["user_id"]:
            return True
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso não autorizado")
