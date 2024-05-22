from schemas import schemas
from fastapi import APIRouter, Request
from services.user_auth_service import UserAuthService
from auth.auth_bearer import token_required, specific_user_token_required

router = APIRouter()
user_auth_services = UserAuthService()

@router.post("/Login", response_model=dict)
async def login(request: Request,form_data: schemas.LoginData):
    return await user_auth_services.create_authentication_token(form_data)

@router.post('/Logout')
@token_required
async def logout(request: Request):
    return await user_auth_services.cancel_authentication_token_by_request(request=request)

@router.post('/ChangePassword')
@token_required
@specific_user_token_required
async def change_password(request: Request, form_data: schemas.ChangePassword):
    return await user_auth_services.change_password(request, form_data)
 
@router.post('/CancelUser')
@token_required
@specific_user_token_required
async def cancel_user(request: Request, form_data: schemas.CancelUser):
    return await user_auth_services.cancel_user(request, form_data)

@router.post('/ForgotPassword')
async def send_password_recuperation_email(request: Request, form_data: schemas.ForgotPassword):
    return await user_auth_services.send_password_recuperation_email(form_data)

@router.get('/ForgotPasswordVerify')
async def verify_forgot_password_code(request: Request, form_data: schemas.VerifyForgotPassword):
    return await user_auth_services.verifiy_forgot_password_code(form_data)

@router.post('/ForgotPasswordChangePassword')
async def forgot_password_change_password(request: Request, form_data: schemas.ForgotPasswordChangePassword):
    return await user_auth_services.forgot_password_change_password(form_data)