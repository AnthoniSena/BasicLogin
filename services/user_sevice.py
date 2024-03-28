from schemas import schemas
from db.models.user import User
from fastapi import HTTPException, status, Request
from datetime import datetime, timezone
from passlib.context import CryptContext
from repository.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self) -> None:
        self.user_repository = UserRepository()
    
    async def create_new_user(self, user_info: schemas.UserInput):
        hashed_password = pwd_context.hash(user_info.password)

        if await self.user_repository.verify_email_registered(user_info.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar usuário. E-mail já cadastrado.")

        new_user = User(
                    name=user_info.name,
                    email=user_info.email,
                    status='A',
                    registration_date=datetime.now(timezone.utc),
                    password=hashed_password)

        new_user_id = await self.user_repository.register_user(user=new_user)

        return {"message": "Usuário criado com sucesso", "user_id": new_user_id}
    
    async def get_user_by_id(self, user_id: int):
        user = await self.user_repository.get_user_info_by_id(user_id=user_id)
        if user.status == "C":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário Cancelado.")
        return user
