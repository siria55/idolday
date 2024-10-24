from fastapi import APIRouter

from .endpoints import xox

api_router = APIRouter()
api_router.include_router(xox.router, tags=["XOX"])
