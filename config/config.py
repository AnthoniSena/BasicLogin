import os
from dotenv import load_dotenv

from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME:str = "Project Name"
    PROJECT_VERSION: str = "1.0.0"

    DATABASE_USER : str = os.getenv("DATABASE_USER","root")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD","6233")
    DATABASE_SERVER : str = os.getenv("DATABASE_SERVER","18.188.227.95")
    DATABASE_PORT : str = os.getenv("DATABASE_PORT",5432)
    DATABASE_DB : str = os.getenv("DATABASE_DB","postgres")
    DATABASE_URL = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_SERVER}:{DATABASE_PORT}/{DATABASE_DB}"

settings = Settings()