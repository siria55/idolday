from fastapi import APIRouter
from .config import router

api_router = APIRouter()
api_router.include_router(router, prefix="/admin", tags=["Admin"])
