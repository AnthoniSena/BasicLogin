from schemas import schemas
from fastapi import APIRouter, Request, HTTPException
from controllers.user_controller import UserController
from db.session import Session
from auth.auth_bearer import token_required

SessionLocal = Session
router = APIRouter()
user_controller = UserController(SessionLocal)

@router.post("/Cadastrar")
def Cadastra_usuario(request: Request,usuario_input: schemas.UserInput):
    name = usuario_input.name
    email = usuario_input.email
    password = usuario_input.password
    return user_controller.create_user(name, email, password)

@router.get("/Usuario/{id_usuario}")
@token_required
async def pega_usuario(request: Request,id_usuario: int):
    # Aqui você pode usar o token JWT para realizar a autenticação e autorização
    user = user_controller.get_user_by_id(id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post('/change-password')
@token_required
def change_password(form_data: schemas.changepassword):
    user = user_controller.get_user(email=form_data.email)
    new_password = form_data.new_password
    if not user:
        raise HTTPException(status_code=400, detail="Usuario não encontrado")
    
    if not user_controller.verify_password(form_data.old_password, user.password):
        raise HTTPException(status_code=400, detail="Senha invalida")

    return user_controller.change_password(user.id, new_password)