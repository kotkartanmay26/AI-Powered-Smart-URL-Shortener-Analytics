
from fastapi import APIRouter
from .auth import router as auth_router
from .urls import router as urls_router
from .analytics import router as analytics_router
from .admin import router as admin_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(urls_router)
api_router.include_router(analytics_router)
api_router.include_router(admin_router)
