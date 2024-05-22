from schemas import schemas
from fastapi import APIRouter, Request
from services.user_service import UserService
from db.session import Session
from auth.auth_bearer import token_required,specific_user_token_required

SessionLocal = Session
router = APIRouter()
user_service = UserService()

@router.post("/UserRegister")
async def register_user(request: Request, user_info_input: schemas.UserInput):
    return await user_service.create_new_user(user_info_input)

@router.get("/User/{user_id}")
@token_required
@specific_user_token_required
async def get_user(request: Request,user_id: int):
    return await user_service.get_user_by_id(user_id)
