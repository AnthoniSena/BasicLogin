from fastapi import HTTPException, status, Request
from schemas import schemas
from datetime import datetime, timezone, timedelta
from repository.user_auth_repository import UserAuthRepository
from mail.mail_sender import MailSender
from utils.utils import encode, decode, verify_password, hash_password, generate_random_code, validate_password
from config.config import settings

class UserAuthService:
    def __init__(self) -> None:
        self.user_auth_repository = UserAuthRepository()

    def _validate_canceled_user(self, user_info: dict) -> bool:
        if user_info["status"] == "C":
            return True
        elif user_info["status"] == "A":
            return False
        
    async def _validade_authentication_token_creation(self, input_info: dict):
        
        if input_info["status"] == "C":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário cancelado.")
        
        if not verify_password({"typed_password": input_info["password"],
                                "registered_password": input_info["hashed_password"]}):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta.")
        
    async def _return_old_authentication_token(self, input_info: dict):
        
        secured_existing_token = encode({"data": input_info["token_info"],
                                        "secret_key": settings.HTTP_ACCESS_TOKEN_SECRET_KEY,
                                        "algorithm": settings.ALGORITHM})
            
        return {
                "message": "Token Criado com sucesso.",
                "Token": secured_existing_token,
                "Type": "Bearer"}

    async def create_authentication_token(self, form_data: schemas.LoginData) -> dict:
        user_info = await self.user_auth_repository.get_user_info_by_email({"email":form_data.email})
        
        if user_info == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        
        try:
            await self._validade_authentication_token_creation({'status': user_info['status'],
                                                                "password": form_data.password,
                                                                "hashed_password": user_info["password"]})
        except HTTPException as e:
            raise e
        
        existing_token_info = await self.user_auth_repository.get_existing_token({"email": form_data.email})

        if existing_token_info['token'] is not None:
            
            return await self._return_old_authentication_token({"token_info": existing_token_info})
        
        acces_token_expire_date = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))

        data = {
            "user_id": user_info["id"],
            "expire_date": acces_token_expire_date.isoformat()
        }

        acces_token = encode({"data":data,
                              "secret_key":settings.JWT_ACCESS_TOKEN_SECRET_KEY,
                              "algorithm": settings.ALGORITHM
                            })
        
        data.update({"token": acces_token})

        if not await self.user_auth_repository.create_new_acces_token(token_data=data):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao cadastrar token de acesso.")

        secured_new_token = encode({"data": {"token": acces_token},
                                    "secret_key": settings.HTTP_ACCESS_TOKEN_SECRET_KEY,
                                    "algorithm": settings.ALGORITHM}
                                    )

        return {"message": "Token Criado com sucesso.",
                "Token": secured_new_token,
                "Type": "Bearer",
                "user_id": user_info["id"]}

    async def cancel_authentication_token_by_request(self, request: Request):
        token = (request.headers.get("Authorization")).split(" ")[1]

        decoded_token = decode({"data":token,
                                "secret_key":settings.HTTP_ACCESS_TOKEN_SECRET_KEY,
                                "algorithm": settings.ALGORITHM})

        if await self.user_auth_repository.cancel_access_token({"token": decoded_token["token"]}):
            return {"message": "Logout efetuado com sucesso."}
        
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao fazer logout.")

    async def change_password(self, request: Request, user_info: schemas.ChangePassword):
        is_new_password_valid = validate_password({"password": user_info.new_password})
        
        if not is_new_password_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nova senha inválida.")
        
        user = await self.user_auth_repository.get_user_info_by_id({"user_id": user_info.user_id})
        
        if user == False:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado.")
        
        is_user_canceled = self._validate_canceled_user({"status": user["status"]})
        
        if is_user_canceled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário cancelado.")
        
        hashed_password = (await self.user_auth_repository.get_user_info_by_email({"email": user["email"]}))["password"]

        if not verify_password({"typed_password": user_info.old_password,
                                "registered_password": hashed_password}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha invalida")
        
        await self.cancel_authentication_token_by_request(request)
                
        hashed_new_password = hash_password({"password": user_info.new_password})
        
        change_password_info = {"user_id": user["id"],
                                "new_password": hashed_new_password["hashed_password"]}

        if not await self.user_auth_repository.change_user_password(change_password_info):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro ao alterar senha.")
        
        return {"message": "Senha Alterada com sucesso."}


    async def cancel_user(self,request: Request, user_info: schemas.CancelUser):
        user = await self.user_auth_repository.get_user_info_by_id({"user_id": user_info.user_id})
        
        is_user_canceled = self._validate_canceled_user({"status": user["status"]})
        
        if is_user_canceled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário já está cancelado.")
        
        await self.cancel_authentication_token_by_request(request)
        
        if not await self.user_auth_repository.cancel_user({"user_id": user["id"]}):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao cancelar usuário.")
        
        return {"message": "Usuário cancelado com sucesso."}


    async def send_password_recuperation_email(self, user_info: schemas.ForgotPassword):
        user = await self.user_auth_repository.get_user_info_by_email({"email": user_info.email})
        
        is_user_canceled = self._validate_canceled_user({"status": user['status']})
        
        if is_user_canceled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário está cancelado.")
        
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email não cadastrado.")

        existing_recuperation_code = await self.user_auth_repository.get_existing_account_recuperation_code({"id": user["id"]})
    
        mail = MailSender()
        
        if existing_recuperation_code["recuperation_code"] is not None:
            existing_code_mail_info = {"send_to": user["email"],
                                        "email_info": existing_recuperation_code["recuperation_code"]}
            
            if await mail.send_forgot_password_email(existing_code_mail_info):
                return {"message": "E-mail enviado com sucesso."}

        is_user_canceled = self._validate_canceled_user(user)
        
        if is_user_canceled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário cancelado.")

        is_valid_recuperation_code = False

        while is_valid_recuperation_code == False:
            recuperation_code = generate_random_code()
            is_valid_recuperation_code = await self.user_auth_repository.verify_existing_account_recuperation_code({"code": recuperation_code})

        account_recuperation_valid_date = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        
        register_recuperation_code_info = {"user_id": user["id"],
                                           "random_string": recuperation_code,
                                           "expire": account_recuperation_valid_date}

        if not await self.user_auth_repository.register_account_recuperation_code(register_recuperation_code_info):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro cadastrar codigo de recuperação")
        
        new_code_mail_info = {"send_to": user["email"],
                              "email_info": recuperation_code}
        
        if await mail.send_forgot_password_email(new_code_mail_info):
            return {"message": "E-mail enviado com sucesso."}

    async def verifiy_forgot_password_code(self, code_info: schemas.VerifyForgotPassword):
        is_valid_forgot_password_code = await self.user_auth_repository.verify_forgot_password({"code": code_info.code})

        if is_valid_forgot_password_code:
            return {"message:": "Código Valido."}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido")

    async def forgot_password_change_password(self, input_info: schemas.ForgotPasswordChangePassword):
        is_new_password_valid = validate_password({"password": input_info.new_password})
        
        if not is_new_password_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha inválida.")
        
        await self.verifiy_forgot_password_code(input_info)
        
        forgot_password_code = {"code": input_info.code}
        
        user_id = await self.user_auth_repository.get_user_id_by_code(forgot_password_code)
        
        if user_id["user_id"] == None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário cancelado")
        
        user_info = await self.user_auth_repository.get_user_info_by_id({"user_id": user_id["user_id"]})
        
        new_password = hash_password({"password": input_info.new_password})["hashed_password"]
        
        change_password_info = {"new_password": new_password,
                     "user_id": user_info["id"]}
        
        existing_token_info = await self.user_auth_repository.get_existing_token({"email": user_info["email"]})
        
        if existing_token_info["token"] is not None:
            if not await self.user_auth_repository.cancel_access_token(existing_token_info):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao cancelar código de acesso.")
        
        if not await self.user_auth_repository.change_user_password(change_password_info):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao trocar senha.")
        
        if not await self.user_auth_repository.cancel_forgot_password_code(forgot_password_code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Erro ao cancelar código.")
        
        return {"message": "Senha alterada com sucesso."}