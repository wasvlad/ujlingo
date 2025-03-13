import os

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from .tools import validate_admin_session
from database.models import User, WordsToUa

router = APIRouter()

class MessageResponse(BaseModel):
    message: str


def words_translations_to_pairs(data: dict) -> list:
    data_converted = []
    for orig, translations in data.items():
        for translated in translations:
            data_converted.append((orig, translated))
    return data_converted

@router.post("/migrate-words-to-ua", response_model=MessageResponse)
async def migrate_words_to_ua(user: User = Depends(validate_admin_session),
                              db: Session = Depends(get_db)):
    url = os.getenv("TRANSLATOR_URL") + "/en-to-ua-words"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    data_converted = words_translations_to_pairs(data)
    words = db.query(WordsToUa).all()
    for word in words:
        if (word.original_word, word.translated_word) in data_converted:
            data_converted.remove((word.original_word, word.translated_word))
        else:
            db.delete(word)
    for or_word, ua_word in data_converted:
        new_word = WordsToUa(original_word=or_word, translated_word=ua_word)
        db.add(new_word)
    db.commit()
    return {"message": "Operation successful"}