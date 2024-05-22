from functools import wraps
from fastapi import Request
from typing import Callable
from fastapi.requests import Request
from services.auth_bearer_service import AuthBearerService

def token_required(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        auth_bearer_service = AuthBearerService()

        await auth_bearer_service.validate_token(request)

        return await func(request,*args, **kwargs)
        
    return wrapper

def specific_user_token_required(func: Callable):
    @wraps(func)
    async def specific_user_wrapper(request: Request, *args, **kwargs):
        auth_bearer_service = AuthBearerService()

        await auth_bearer_service.validate_specific_user_token(request, kwargs)

        return await func(request,*args, **kwargs)
    
    return specific_user_wrapper