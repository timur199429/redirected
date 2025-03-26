from fastapi import APIRouter

from src.routers.nutra import nutra_router
from src.routers.vitrina import vitrina_router
from src.routers.clickback import clickback


main_router = APIRouter()
main_router.include_router(nutra_router)
main_router.include_router(vitrina_router)
main_router.include_router(clickback)


