import jwt
import random
import string
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encode(to_encode_info: dict) -> dict:
        return jwt.encode(
            to_encode_info["data"],
            to_encode_info["secret_key"],
            to_encode_info["algorithm"]
        )

def decode(to_decode_info:dict):
    try:
        decoded_acces_token = jwt.decode(
            to_decode_info["data"],
            to_decode_info["secret_key"],
            to_decode_info["algorithm"])

        return decoded_acces_token
    except InvalidTokenError:
        return None
    
def verify_password(passwords_info: dict) -> bool:
    return pwd_context.verify(passwords_info["typed_password"], passwords_info["registered_password"])

def hash_password(to_hash_info: dict) -> dict:
    hashed_content = {"hashed_password":pwd_context.hash(to_hash_info["password"])}
    return hashed_content

def generate_random_code() -> str:
    char_list = string.ascii_uppercase + string.digits

    return (''.join(random.choice(char_list) for _ in range(8)))

def validate_password(info: dict) -> bool:
    if len(info["password"]) < 8 or len(info["password"]) > 16:
        return False
    
    if not re.search("[a-z]", info["password"]):
        return False
    
    if not re.search("[A-Z]", info["password"]):
        return False

    if not re.search("[0-9]", info["password"]):
        return False
    
    return True

def validate_email(info: dict):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", info["email"]):
        return False
    
    return True

def validate_nickname(info: dict) -> bool:
    if len(info["nick_name"]) < 4 or len(info["nick_name"]) > 16:
        return False    
    
    return True