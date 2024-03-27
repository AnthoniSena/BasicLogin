from db.models.user import User
from fastapi import HTTPException, status
from db.models.authentication_token import AuthenticationToken
from datetime import datetime, timezone, timedelta
import jwt
import os

HTTP_ACCESS_TOKEN_SECRET_KEY = os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_SECRET_KEY = os.getenv("JWT_ACCESS_TOKEN_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

class AuthenticationTokenController:
    def __init__(self, SessionLocal) -> None:
        self.SessionLocal = SessionLocal

    def validate_token(self, token: str):
        session = self.SessionLocal()
        exist_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.access_token==token,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)).first()
        session.close()
        if exist_token:
            return True
        return False
        
    def exist_valid_token_user(self, user:User):
        session = self.SessionLocal()
        exist_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.user_id==user.id,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)
            ).first()
        session.close()
        if exist_token:
            return exist_token
        else:
            return False

    def exist_valid_token(self, token:str):
        session = self.SessionLocal()
        exist_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.access_token==token,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)
            ).first()
        session.close()
        if exist_token:
            return exist_token
        else:
            return False

    async def create_access_token(self, user: User):
        session = self.SessionLocal()
        
        existing_token = self.exist_valid_token_user(user=user)
        if existing_token:
            return existing_token
        
        data = {"sub": user.email}
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        data.update({"exp": expire})
        acces_token = jwt.encode(data, ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
        new_data = {"token": acces_token}
        secured_acces_token = jwt.encode(new_data, HTTP_ACCESS_TOKEN_SECRET_KEY, algorithm=ALGORITHM)
        new_token = AuthenticationToken(creation_date=datetime.now(timezone.utc), expiration_date=expire, user_id=user.id, access_token=acces_token, status="A", refresh_token="dasdwakdjw")
        
        session.add(new_token)

        try:
            session.commit()
            session.refresh(new_token)
            return secured_acces_token
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar token de acesso.") from e
        finally:
            session.close()

    async def cancel_access_token(self, token: str):
        session = self.SessionLocal()
        if not self.validate_token(token):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Token não encontrado.")

        existing_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.access_token==token,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)
            ).first()
        existing_token.status="C"
        try:
            session.commit()
            return {"message": "Logout efetuado com sucesso."}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao alterar senha.") from e
        finally:
            session.close()
