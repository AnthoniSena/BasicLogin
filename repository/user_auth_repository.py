from fastapi import HTTPException, status
from db.session import Session
from db.models.user import User
from datetime import datetime, timezone
from db.models.authentication_token import AuthenticationToken

class UserAuthRepository():

    async def get_user_info(self, email: str) -> User:
        session = Session()

        user = session.query(User).filter(User.email == email).first()
        session.close()
        return user

    async def get_user_info_by_id(self, user_id: str) -> User:
        session = Session()

        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        if user:
            return user
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    async def validate_registered_email(self, email: str) -> bool:
        session = Session()

        if session.query(User).filter(User.email == email).first():
            session.close()
            return True
        session.close()
        return False
    
    async def get_hashed_password(self, email: str) -> str:
        hashed_password = (await self.get_user_info(email=email)).password
        if hashed_password:
            return hashed_password
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")

    async def get_existing_token(self, email: str):
        session = Session()

        user_id = (await self.get_user_info(email=email)).id
        exist_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.user_id==user_id,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)
            ).first()
        session.close()
        if exist_token:
            return exist_token
        return False

    async def create_new_acces_token(self, token_data: dict):
        session = Session()

        new_token = AuthenticationToken(
                        creation_date=datetime.now(timezone.utc),
                        expiration_date=token_data["exp"],
                        user_id=token_data["user_id"],
                        access_token=token_data["token"],
                        status="A")
        
        session.add(new_token)

        try:
            session.commit()
            return token_data["token"]
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao criar token de acesso.") from e
        finally:
            session.close()

    async def cancel_access_token(self, token= str):
        session = Session()

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

    async def change_user_password(self, user_id: int, new_password: str):
        session = Session()
        user = session.query(User).filter_by(id=user_id).first()
        user.password = new_password
        try:
            session.commit()
            session.refresh(user)
            return {"message": "Senha alterada com sucesso."}
        except Exception as e:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao alterar senha.") from e
        finally:
            session.close()
