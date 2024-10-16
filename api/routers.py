from fastapi import APIRouter
from .endpoints import user, login, register, system
from .device.device import router as device_router

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["Users"])
api_router.include_router(login.router, tags=["Login"])
api_router.include_router(register.router, tags=["Register"])
api_router.include_router(device_router, prefix="/devices", tags=["Device"])
# api_router.include_router(system.router, prefix="/system", tags=["System"])
