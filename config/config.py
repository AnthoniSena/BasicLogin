import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME:str = "Project Name"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_URL : str =  os.getenv("DATABASE_URL")
    HTTP_ACCESS_TOKEN_SECRET_KEY : str = os.getenv("HTTP_ACCESS_TOKEN_SECRET_KEY")
    JWT_ACCESS_TOKEN_SECRET_KEY : str = os.getenv("JWT_ACCESS_TOKEN_SECRET_KEY")
    ALGORITHM : str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES : str = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    ACCOUNT_RECUPERATION_EXPIRE_MINUTES : str = os.getenv("ACCOUNT_RECUPERATION_EXPIRE_MINUTES")
    MAIL_ADDRESS : str  = os.getenv("MAIL")
    MAIL_PASSWORD : str = os.getenv("MAIL_PASSWORD")
    ALGORITHM = os.getenv("JWT_ALGORITHM")

settings = Settings()
