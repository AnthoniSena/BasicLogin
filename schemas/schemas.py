from pydantic import BaseModel, EmailStr

class LoginData(BaseModel):
    email: str
    password: str

class UserInput(BaseModel):
    name: str
    email: EmailStr
    password: str

class changepassword(BaseModel):
    user_id:str
    old_password:str
    new_password:str
