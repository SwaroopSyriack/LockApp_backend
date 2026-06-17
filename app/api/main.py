from fastapi import APIRouter
from app.api.routes import users,login,tables



api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(login.router)
api_router.include_router(tables.router)






