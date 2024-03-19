from core.config import settings
from fastapi import FastAPI, Depends
from db.session import engine 
from db.models.user import User
from db.models.authentication_token import AuthenticationToken
from db.session import Session
import os
from fastapi import HTTPException
from controllers.user_controller import UserController
from schema.schemas import UserInput, LoginData

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
def Cadastra_usuario(usuario_input: UserInput):
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
async def login_access_token(form_data: LoginData):
    user = user_controller.get_user(email=form_data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    access_token = user_controller.create_authentication_token(email=form_data.email, password=form_data.password)
    return {"token": access_token.access_token, "token_type": "bearer"}

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", port=5734, host="0.0.0.0", log_level="info", reload=True)