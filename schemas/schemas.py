from pydantic import BaseModel, EmailStr

class LoginData(BaseModel):
    email: str
    password: str

class UserInput(BaseModel):
    name: str
    nick_name: str
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    user_id:str
    old_password:str
    new_password:str

class CancelUser(BaseModel):
    user_id:str

class ForgotPassword(BaseModel):
    email: str

class VerifyForgotPassword(BaseModel):
    code: str

class ForgotPasswordChangePassword(BaseModel):
    code: str
    new_password: str