from schemas import schemas
from fastapi import APIRouter, Request
from services.user_auth_service import UserAuthService
from db.session import Session
from auth.auth_bearer import token_required, specific_user_token_required

SessionLocal = Session
router = APIRouter()
user_auth_services = UserAuthService()

@router.post("/login", response_model=dict)
async def login(request: Request,form_data: schemas.LoginData):
    return await user_auth_services.create_authentication_token(form_data)

@router.post('/logout')
@token_required
def logout(request: Request):
    return user_auth_services.cancel_authentication_token(request=request)

@router.post('/ChangePassword')
@token_required
@specific_user_token_required
async def change_password(request: Request, form_data: schemas.changepassword):
    return await user_auth_services.change_password(form_data)