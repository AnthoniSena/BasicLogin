from fastapi import HTTPException, status
from db.session import Session
from db.models.user import User
from datetime import datetime, timezone, timedelta
from db.models.authentication_token import AuthenticationToken
from schemas import schemas
import os
import jwt

HTTP_ACCESS_TOKEN_SECRET_KEY = os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_SECRET_KEY = os.getenv("JWT_ACCESS_TOKEN_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

class UserRepository():

    async def verify_email_registered(self, email: str) -> User:
        session = Session()

        user = session.query(User).filter(User.email == email).first()
        session.close()
        if user:
            return True
        return False

    async def register_user(self, user: User):
        session = Session()

        session.add(user)
        try:
            session.commit()
            return user.id
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar usuário.") from e
        finally:
            session.close()

    async def get_user_info_by_id(self, user_id: int) -> User:
        session = Session()

        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
        session.close()
        return user