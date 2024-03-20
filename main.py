from core.config import settings
from fastapi import FastAPI, Depends
from db.session import engine 
from db.models.user import User
from db.models.authentication_token import AuthenticationToken
from db.session import Session
import os
from fastapi import HTTPException
from controllers.user_controller import UserController
from schema import schemas 

SessionLocal = Session

user_controller = UserController(SessionLocal)

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

def create_tables():
    User.metadata.create_all(bind=engine)
    AuthenticationToken.metadata.create_all(bind=engine)

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
    create_tables()
    return app

app = start_application()

@app.post("/Cadastrar")
def Cadastra_usuario(usuario_input: schemas.UserInput):
    name = usuario_input.name
    email = usuario_input.email
    password = usuario_input.password
    return user_controller.create_user(name, email, password)

@app.get("/Usuario/{id_usuario}")
def pega_usuario(id_usuario: int):
    user = user_controller.get_user_by_id(id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@app.post("/login", response_model=dict)
async def login_access_token(form_data: schemas.LoginData):
    user = user_controller.get_user(email=form_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = user_controller.create_authentication_token(email=form_data.email, password=form_data.password)
    return {"token": access_token.access_token, "token_type": "bearer"}

@app.post('/change-password')
def change_password(form_data: schemas.changepassword):
    user = user_controller.get_user(email=form_data.email)
    new_password = form_data.new_password
    if not user:
        raise HTTPException(status_code=400, detail="Usuario não encontrado")
    
    if not user_controller.verify_password(form_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Senha invalida")

    return user_controller.change_password(user.id, new_password)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", port=5734, host="0.0.0.0", log_level="info", reload=True)