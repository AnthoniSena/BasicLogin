from db.models.user import User
from fastapi import HTTPException
from db.models.authentication_token import AuthenticationToken
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

class AuthenticationTokenController:
    def __init__(self, SessionLocal) -> None:
        self.SessionLocal = SessionLocal

    def validate_token(self, token: str):
        session = self.SessionLocal()
        exist_token = session.query(AuthenticationToken).filter(AuthenticationToken.access_token==token, AuthenticationToken.status=="A", AuthenticationToken.expiration_date > datetime.now(timezone.utc)).first()
        if exist_token:
            return True
        return False
    
    def exist_valid_token(self, user:User):
        session = self.SessionLocal()
        exist_token = session.query(AuthenticationToken).filter(AuthenticationToken.user_id==user.id, AuthenticationToken.status=="A", AuthenticationToken.expiration_date > datetime.now(timezone.utc)).first()
        if exist_token:
            return exist_token
        else:
            return False

    def create_access_token(self, user: User):
        session = self.SessionLocal()
        authentication_token = AuthenticationTokenController(self.SessionLocal)
        
        existing_token = authentication_token.exist_valid_token(user=user)
        if existing_token:
            return existing_token
        
        data = {"sub": user.email}
        expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
        data.update({"exp": expire})
        encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        new_token = AuthenticationToken(creation_date=datetime.now(timezone.utc), expiration_date=expire, user_id=user.id, access_token=encoded_jwt, status="A")
        
        session.add(new_token)

        try:
            session.commit()
            session.refresh(new_token)
            return new_token
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=400, detail="Erro ao criar token de acesso.") from e
        finally:
            session.close()
