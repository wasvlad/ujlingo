from fastapi import APIRouter

from . import words, sentences

router = APIRouter()
router.include_router(words.router, prefix="/words")
router.include_router(sentences.router, prefix="/sentences")

