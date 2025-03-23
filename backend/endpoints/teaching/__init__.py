from fastapi import APIRouter
from . import random

router = APIRouter()
router.include_router(random.router, prefix="/random")
