from fastapi import APIRouter

from .endpoints import xox
from .admin import xox as admin_xox

api_router = APIRouter()
api_router.include_router(xox.router, tags=["XOX"])

api_router.include_router(admin_xox.router, tags=["Admin"])
