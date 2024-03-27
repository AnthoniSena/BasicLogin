from db.models.user import User
from fastapi import HTTPException, status, Request
from datetime import datetime, timezone
from passlib.context import CryptContext
from .authentication_token_controller import AuthenticationTokenController
from auth.auth_bearer import decode_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserController:
    def __init__(self, SessionLocal) -> None:
        self.SessionLocal = SessionLocal

    def get_user_by_id(self, user_id):
        session = self.SessionLocal()
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        
        session.close()
        return user

    def create_user(self, nome: str, email: str, password: str) -> User:
        session = self.SessionLocal()
        if self.exist_user(email=email):
            return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar usuário. E-mail já cadastrado.")
        hashed_password = pwd_context.hash(password)
        new_user = User(name=nome, email=email, status='A', registration_date=datetime.now(timezone.utc), password=hashed_password)
        session.add(new_user)
        try:
            session.commit()
            return {"message": "Usuário criado com sucesso", "user_id": new_user.id}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao criar usuário.") from e
        finally:
            session.close()
        
    def exist_user(self, email:str):
        session = self.SessionLocal()
        user = session.query(User).filter(User.email == email).first()
        session.close()
        if user:
            return True
        return False
        
    def get_user(self, email: str):
        session = self.SessionLocal()
        user = session.query(User).filter(User.email == email).first()
        session.close()
        if user.status != 'A':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário cancelado.")
        elif user:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
            
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    async def create_authentication_token(self, email: str, password: str):
        authentication_token = AuthenticationTokenController(self.SessionLocal)
        user = self.get_user(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")
        if not self.verify_password(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta.")
        exist_token = authentication_token.exist_valid_token_user(user=user)
        if exist_token:
            return exist_token
        else:
            token = authentication_token.create_access_token(user=user)
        return token
    
    async def invalidate_authentication_token(self, request: Request):
        authentication_token = AuthenticationTokenController(self.SessionLocal)
        bearer_token = request.headers.get("Authorization")
        token = bearer_token.split(" ")[1]
        decoded_token = decode_access_token(token)
        return await authentication_token.cancel_access_token(token=decoded_token["token"])
    
    async def change_password(self, user_id: int, new_password: str):
        session = self.SessionLocal()
        encrypted_password = pwd_context.hash(new_password)
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        user.password = encrypted_password
        try:
            session.commit()
            return {"message": "Senha Alterada"}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao alterar senha.") from e
        finally:
            session.close()