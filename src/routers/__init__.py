from fastapi import APIRouter

from src.routers.nutra import nutra_router
from src.routers.vitrina import vitrina_router


main_router = APIRouter()
main_router.include_router(nutra_router)
main_router.include_router(vitrina_router)

