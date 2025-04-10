from fastapi import APIRouter
from . import random, test

router = APIRouter()
router.include_router(random.router, prefix="/random")
router.include_router(test.router, prefix="/test")
