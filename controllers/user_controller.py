from db.models.user import User
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from .authentication_token_controller import AuthenticationTokenController
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")


class UserController:
    def __init__(self, SessionLocal) -> None:
        self.SessionLocal = SessionLocal

    def get_user_by_id(self, user_id):
        session = self.SessionLocal()
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        session.close()
        return user

    def create_user(self, nome: str, email: str, password: str) -> User:
        session = self.SessionLocal()
        if self.exist_user(email=email):
            return HTTPException(status_code=400, detail="Erro ao criar usuário. E-mail já cadastrado.")
        hashed_password = pwd_context.hash(password)
        new_user = User(name=nome, email=email, status='A', registration_date=datetime.now(timezone.utc), password=hashed_password)
        session.add(new_user)
        try:
            session.commit()
            return {"message": "Usuário criado com sucesso", "user_id": new_user.id}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail="Erro ao criar usuário.") from e
        
    def exist_user(self, email:str):
        session = self.SessionLocal()
        user = session.query(User).filter(User.email == email).first()
        if user:
            return True
        return False
        
    def get_user(self, email: str):
        session = self.SessionLocal()
        user = session.query(User).filter(User.email == email).first()
        if user.status != 'A':
            raise HTTPException(status_code=400, detail="Usuário cancelado.")
        elif user:
            return user
        else:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
            
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def create_authentication_token(self, email: str, password: str):
        authentication_token = AuthenticationTokenController(self.SessionLocal)
        user = self.get_user(email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuário não encontrado.")
        if not self.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Senha incorreta.")
        exist_token = authentication_token.exist_valid_token(user=user)
        if exist_token:
            return exist_token
        else:
            token = authentication_token.create_access_token(user=user)
        return token
    
    def change_password(self, user_id: int, new_password: str):
        session = self.SessionLocal()
        encrypted_password = pwd_context.hash(new_password)
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        user.password = encrypted_password
        try:
            session.commit()
            return {"message": "Senha Alterada"}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail="Erro ao alterar senha.") from e
        finally:
            session.close()

    
    def validate_token(self, token):
        pass