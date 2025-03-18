from fastapi import APIRouter

from . import words


router = APIRouter()
router.include_router(words.router)