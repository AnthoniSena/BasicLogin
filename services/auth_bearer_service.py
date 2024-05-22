from repository.auth_bearer_repository import AuthBearerRepository
from fastapi import Request, HTTPException, status
from config.config import settings
from utils.utils import decode

class AuthBearerService:
    def __init__(self) -> None:
        self.auth_bearer_repository = AuthBearerRepository()

    async def validate_token(self, request: Request) -> bool:
        bearer_token = request.headers.get("Authorization")

        if bearer_token == None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token de autenticação não fornecido.")
        
        token_value = bearer_token.split(" ")[1]

        decoded_token = decode({"data": token_value,
                                "secret_key": settings.HTTP_ACCESS_TOKEN_SECRET_KEY,
                                "algorithm": settings.ALGORITHM})

        if decoded_token == None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação inválido")
         
        token = decode({"data": str(decoded_token["token"]),
                        "secret_key": settings.JWT_ACCESS_TOKEN_SECRET_KEY,
                        "algorithm": settings.ALGORITHM})
        
        is_user_canceled = await self.auth_bearer_repository.validate_canceled_user({"user_id": token["user_id"]})
        
        if is_user_canceled:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário cancelado.")
         
        valid_token = await self.auth_bearer_repository.validate_token(token=decoded_token["token"])
        
        if valid_token:
            return True
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação inválido")

    async def validate_specific_user_token(self, request: Request, kwargs: dict) -> bool:
        if 'form_data' in kwargs:
            user_id = dict(kwargs["form_data"])["user_id"]
        elif 'user_id' in kwargs:
            user_id = kwargs["user_id"]
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Id de usuário não fornecido.")
        
        coded_token = request.headers.get("Authorization").split(" ")[1]

        token = decode({"data": coded_token,
                        "secret_key": settings.HTTP_ACCESS_TOKEN_SECRET_KEY,
                        "algorithm": settings.ALGORITHM})

        token = decode({"data": str(token["token"]),
                        "secret_key": settings.JWT_ACCESS_TOKEN_SECRET_KEY,
                        "algorithm": settings.ALGORITHM})

        if int(user_id) == int(token["user_id"]):
            return True
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Acesso não autorizado")
