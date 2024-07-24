from fastapi import APIRouter
from .endpoints import user, login, register, nlp

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(register.router, prefix="/register", tags=["Register"])
api_router.include_router(nlp.router, prefix="/npl", tags=["NPL"])
