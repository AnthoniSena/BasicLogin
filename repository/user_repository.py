from db.session import Session
from db.models.user import User

class UserRepository():

    async def verify_email_registered(self, user_info: dict) -> bool:
        session = Session()

        user = session.query(User).filter(User.email == user_info["email"]).first()
        session.close()
        if user:
            return True
        return False
    
    async def verify_nickname_registered(self, user_info: dict) -> bool:
        session = Session()

        user = session.query(User).filter(User.nick_name == user_info["nick_name"]).first()
        session.close()
        if user:
            return True
        return False

    async def get_user_info_by_id(self, user_id: int) -> dict:
        session = Session()

        user = session.query(User).filter(User.id == user_id).first()
        
        if user == None:
            return False
        
        session.close()
        
        user_info = {
            "name": user.name,
            "nick_name": user.nick_name,
            "email": user.email,
            "status": user.status,
            "registration_date": user.registration_date
        }
        return user_info

    async def register_user(self, user_data: dict):
        session = Session()

        new_user = User(**user_data)

        session.add(new_user)
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()

    async def change_user_nickname(self, user_info: dict):
        session = Session()

        user = session.query(User).filter(User.id == user_info['user_id']).first()
        
        user.nick_name = user_info['nick_name']
        
        try:
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            return False
        finally:
            session.close()