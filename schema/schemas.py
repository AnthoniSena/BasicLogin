from pydantic import BaseModel, EmailStr

class LoginData(BaseModel):
    email: str
    password: str

class UserInput(BaseModel):
    name: str
    email: EmailStr
    password: str