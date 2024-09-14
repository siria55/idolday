from fastapi import APIRouter
from .endpoints import user, login, register
from .device.routers import router as device_router

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(login.router, prefix="/login", tags=["Login"])
api_router.include_router(register.router, prefix="/register", tags=["Register"])
api_router.include_router(device_router, prefix="/devices", tags=["Device"])