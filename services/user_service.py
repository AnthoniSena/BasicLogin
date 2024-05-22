from schemas import schemas
from fastapi import HTTPException, status
from datetime import datetime, timezone
from db.models.user import User
from repository.user_repository import UserRepository
from utils.utils import (hash_password, validate_password, validate_nickname, validate_email)

class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
        
    async def _validate_user_info(self, user_info):
        if not validate_password({"password": user_info.password}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha inválida.")
        
        if not validate_nickname({"nick_name": user_info.nick_name}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apelido inválido.")
        
        if not validate_email({"email": user_info.email}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail inválido.")
        
        if await self.user_repository.verify_email_registered({"email": user_info.email}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado.")
        
        if await self.user_repository.verify_nickname_registered({"nick_name": user_info.nick_name}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apelido já cadastrado.")
    
    async def create_new_user(self, user_info: schemas.UserInput):

        try:
            await self._validate_user_info(user_info)
        except HTTPException as e:
            raise e
        
        hashed_password = hash_password({"password": user_info.password})
        
        new_user_data = {
            "name": user_info.name,
            "nick_name": user_info.nick_name,
            "email": user_info.email,
            "status": 'A',
            "registration_date": datetime.now(timezone.utc),
            "password": hashed_password["hashed_password"]}

        if await self.user_repository.register_user(new_user_data):
            return {"message": "Usuário criado com sucesso"}
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar usuário.")
    
    async def get_user_by_id(self, user_id: int):
        user_info = await self.user_repository.get_user_info_by_id(user_id=user_id)
        
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
        if user_info["status"] == 'C':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário cancelado.")
        
        return user_info
    