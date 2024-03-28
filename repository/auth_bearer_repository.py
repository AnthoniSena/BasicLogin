from db.models.authentication_token import AuthenticationToken
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