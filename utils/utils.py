import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encode(to_encode, key, algorithm):
    return jwt.encode(to_encode, key, algorithm)

def decode(to_decode, key, algorithm):
    try:
        decoded_acces_token = jwt.decode(to_decode, key, algorithm)
        return decoded_acces_token
    except InvalidTokenError:
        return None
    
def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)