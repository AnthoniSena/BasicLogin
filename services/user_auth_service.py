from fastapi import HTTPException, status, Request
from schemas import schemas
from datetime import datetime, timezone, timedelta
from repository.user_auth_repository import UserAuthRepository
from utils.utils import encode, decode, verify_password, hash_password
import os

HTTP_ACCESS_TOKEN_SECRET_KEY = os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_SECRET_KEY = os.getenv("JWT_ACCESS_TOKEN_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

class UserAuthService:
    def __init__(self) -> None:
        self.user_auth_repository = UserAuthRepository()

    async def create_authentication_token(self, form_data: schemas.LoginData):

        if not await self.user_auth_repository.validate_registered_email(form_data.email):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        
        token_user = await self.user_auth_repository.get_user_info(email=form_data.email)
        
        hashed_password = await self.user_auth_repository.get_hashed_password(form_data.email)
        
        if not verify_password(form_data.password, hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta.")
        
        existing_token = await self.user_auth_repository.get_existing_token(form_data.email)

        if existing_token:
            existing_token_data = {"token": existing_token.access_token}
            secured_old_token = encode(existing_token_data, HTTP_ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
            existing_toke_data = {
                "message": "Token Criado com sucesso.",
                "Token": secured_old_token,
                "Type": "Bearer"}
            return existing_toke_data
        

        acces_token_expire_date = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))

        data =  {
                "user_id": token_user.id,
                "exp": acces_token_expire_date
                }
        
        acces_token = encode(data, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
        
        data.update({"token": acces_token})

        new_token = await self.user_auth_repository.create_new_acces_token(token_data=data)

        secured_new_token = encode({"token": new_token}, HTTP_ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)

        return {"message": "Token Criado com sucesso.",
                "Token": secured_new_token,
                "Type": "Bearer"}

    async def cancel_authentication_token(self, request: Request):
        bearer_token = request.headers.get("Authorization")
        token = bearer_token.split(" ")[1]

        decoded_token = decode(token, HTTP_ACCESS_TOKEN_SECRET_KEY, ALGORITHM)

        return await self.user_auth_repository.cancel_access_token(token=decoded_token["token"])

    
    async def change_password(self, info: schemas.changepassword):
        user = await self.user_auth_repository.get_user_info_by_id(user_id=info.user_id)
        if user.status == "C":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário Cancelado.")
        
        hashed_password = await self.user_auth_repository.get_hashed_password(email=user.email)

        if not verify_password(info.old_password, hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha invalida")
        
        hashed_new_password = hash_password(password=info.new_password)

        return await self.user_auth_repository.change_user_password(user.id, hashed_new_password)