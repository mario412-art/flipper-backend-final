from fastapi import APIRouter
from app.api.v1.endpoints import valuations

api_router = APIRouter()
api_router.include_router(valuations.router, prefix="/valuations", tags=["valuations"])
