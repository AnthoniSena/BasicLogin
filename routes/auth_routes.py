from schemas import schemas
from fastapi import APIRouter, Request, HTTPException, status
from controllers.user_controller import UserController
from db.session import Session
from auth.auth_bearer import token_required

SessionLocal = Session
router = APIRouter()
user_controller = UserController(SessionLocal)

@router.post("/login", response_model=dict)
async def login(request: Request,form_data: schemas.LoginData):
    user = user_controller.get_user(email=form_data.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    access_token = user_controller.create_authentication_token(email=form_data.email, password=form_data.password)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/logout')
@token_required
def logout(request: Request):
    return user_controller.invalidate_authentication_token(request=request)