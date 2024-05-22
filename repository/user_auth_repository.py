from db.session import Session
from db.models.user import User
from datetime import datetime, timezone
from db.models.authentication_token import AuthenticationToken
from db.models.account_recuperation import AccountRecuperation

class UserAuthRepository():

    async def get_user_info_by_email(self, user_info: dict) -> dict:
        session = Session()

        user = session.query(User).filter(User.email == user_info["email"]).first()
        
        if user == None:
            return False
        
        user_info = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "status": user.status,
            "registration_date": user.registration_date,
            "password": user.password
        }
        
        session.close()
        return user_info

    async def get_user_info_by_id(self, user_info: dict) -> User:
        session = Session()

        user = session.query(User).filter(
            User.id == user_info["user_id"],
            User.status == "A"
        ).first()
        
        
        if user == None:
            return False
        
        session.close()
        
        user_info = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "status": user.status,
            "registration_date": user.registration_date,
            "hashed_password": user.password
        }
        
        return user_info

    async def get_existing_token(self, user_info: dict):
        session = Session()

        user_id = (await self.get_user_info_by_email({"email": user_info["email"]}))["id"]
        
        exist_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.user_id==user_id,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)
            ).first()
        
        session.close()
        
        if exist_token:
            return {'token': exist_token.access_token}
        return {'token': None}

    async def create_new_acces_token(self, token_data: dict):
        session = Session()

        new_token = AuthenticationToken(
                        creation_date=datetime.now(timezone.utc),
                        expiration_date=token_data["expire_date"],
                        user_id=token_data["user_id"],
                        access_token=token_data["token"],
                        status="A")
        
        session.add(new_token)

        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    async def cancel_access_token(self, token_info: dict) -> dict:
        session = Session()

        existing_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.access_token==token_info["token"],
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)
            ).first()
        
        if existing_token is not None:
            existing_token.status="C"

        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    async def change_user_password(self, user_info: dict) -> dict:
        session = Session()
        user = session.query(User).filter_by(id=user_info["user_id"]).first()
        
        user.password = user_info["new_password"]
        
        try:
            session.commit()
            session.refresh(user)
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()
            
            
    async def cancel_user(self, user_info: dict) -> dict:
        session = Session()
        
        user = session.query(User).filter_by(id=user_info["user_id"]).first()
        
        user.status = 'C'
        
        try:
            session.commit()
            session.refresh(user)
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    async def verify_existing_account_recuperation_code(self, input_info: dict) -> bool:
        session = Session()
        
        equal_recuperation_code = session.query(AccountRecuperation).filter(
            AccountRecuperation.validation_string == input_info["code"],
            AccountRecuperation.expiration_date > datetime.now(timezone.utc)).first()
        
        session.close()
        
        if equal_recuperation_code == None:
            return True
        return False
    
    async def get_existing_account_recuperation_code(self, input_info: dict):
        session = Session()
        
        existing_code = session.query(AccountRecuperation).filter(
            AccountRecuperation.user_id==input_info["id"],
            AccountRecuperation.status=="A",
            AccountRecuperation.expiration_date > datetime.now(timezone.utc)
            ).first()
        
        if existing_code:
            return {"recuperation_code": existing_code.validation_string}
        
        session.close()
        
        return {"recuperation_code": None}

    async def register_account_recuperation_code(self, accounte_recuperation_code_info: dict):
        session = Session()
        new_account_recuperation_code = AccountRecuperation(
                        creation_date=datetime.now(timezone.utc),
                        expiration_date=accounte_recuperation_code_info["expire"],
                        user_id=accounte_recuperation_code_info["user_id"],
                        validation_string=accounte_recuperation_code_info["random_string"],
                        status="A"
        )
        
        session.add(new_account_recuperation_code)

        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    async def verify_forgot_password(self, input_info: dict) -> bool:
        session = Session()
        exist_valid_code = session.query(AccountRecuperation).filter(
            AccountRecuperation.status == "A",
            AccountRecuperation.expiration_date > datetime.now(timezone.utc),
            AccountRecuperation.validation_string == input_info["code"]
        ).first()
        
        session.close()
        
        if exist_valid_code:
            return True
        else:
            return False
        
    async def get_user_id_by_code(self, code_info: dict) -> dict:
        session = Session()
        
        token_info = session.query(AccountRecuperation).filter(
            AccountRecuperation.status == "A",
            AccountRecuperation.expiration_date > datetime.now(timezone.utc),
            AccountRecuperation.validation_string == code_info["code"]
        ).first()
        
        session.close()
        
        if token_info:
            return {"user_id": token_info.user_id}
        
        return {"user_id": None}

    async def cancel_forgot_password_code(self, code_info: dict) -> dict:
        session = Session()
        
        existing_code = session.query(AccountRecuperation).filter(
            AccountRecuperation.status == "A",
            AccountRecuperation.expiration_date > datetime.now(timezone.utc),
            AccountRecuperation.validation_string == code_info["code"]
        ).first()
        
        existing_code.status = 'C'
        
        try:
            session.commit()
            session.refresh(existing_code)
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()