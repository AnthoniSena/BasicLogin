from config.config import settings
from fastapi import FastAPI
from db.session import engine 
from db.models.user import User
from db.models.authentication_token import AuthenticationToken
from db.session import Session
from controllers.user_controller import UserController
from routes import user_routes, auth_routes

SessionLocal = Session

user_controller = UserController(SessionLocal)

def create_tables():
    User.metadata.create_all(bind=engine)
    AuthenticationToken.metadata.create_all(bind=engine)

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME,version=settings.PROJECT_VERSION)
    create_tables()
    return app

app = start_application()

app.include_router(user_routes.router)
app.include_router(auth_routes.router)

import uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", port=5734, host="0.0.0.0", log_level="info", reload=True)