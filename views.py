from fastapi import APIRouter
from routers.ping import router as ping_router

api_router = APIRouter()
api_router.include_router(ping_router)
