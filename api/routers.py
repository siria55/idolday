from fastapi import APIRouter, Depends
from .endpoints import xox
from database import get_db

api_router = APIRouter()
api_router.include_router(xox.router, tags=["XOX"])
