from fastapi import APIRouter
from . import register
from . import login


router = APIRouter()
router.include_router(register.router)
router.include_router(login.router)
