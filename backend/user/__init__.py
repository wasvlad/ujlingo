from fastapi import APIRouter
from . import register


router = APIRouter()
router.include_router(register.router)