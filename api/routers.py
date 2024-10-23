from fastapi import APIRouter
from .endpoints import login, register, system, user_profile, user_devices
from .device.device import router as device_router

api_router = APIRouter()
# api_router.include_router(user_profile.router, tags=["User Profile"])
# api_router.include_router(user_devices.router, tags=["User Devices"])
# api_router.include_router(login.router, tags=["Login"])
# api_router.include_router(register.router, tags=["Register"])
# api_router.include_router(system.router, tags=["System"])

# api_router.include_router(device_router, tags=["Device | 固件接口"])