from fastapi import APIRouter
from . import user
from . import admin


router = APIRouter()
router.include_router(user.router, prefix="/user")
router.include_router(admin.router, prefix="/admin")
