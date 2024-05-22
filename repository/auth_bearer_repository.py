from db.models.authentication_token import AuthenticationToken
from db.models.user import User
from datetime import datetime, timezone
from db.session import Session

class AuthBearerRepository():

    async def validate_token(self, token: str):
        session = Session()
        
        exist_valid_token = session.query(AuthenticationToken).filter(
            AuthenticationToken.access_token==token,
            AuthenticationToken.status=="A",
            AuthenticationToken.expiration_date > datetime.now(timezone.utc)).first()
        
        session.close()

        if exist_valid_token == None:
            return False
        return True
    
    async def validate_canceled_user(self, user_info: dict) -> bool:
        session = Session()
        
        user = session.query(User).filter(
            User.id == user_info["user_id"]
        ).first()
        
        if user.status == "C":
            return True
        else:
            return False