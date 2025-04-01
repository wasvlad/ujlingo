from fastapi import APIRouter
from . import register
from . import login, account, password_reset


router = APIRouter()
router.include_router(register.router)
router.include_router(login.router)
router.include_router(account.router)
router.include_router(password_reset.router)
