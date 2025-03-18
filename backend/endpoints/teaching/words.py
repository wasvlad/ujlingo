from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, List

from sqlalchemy import func

from database import get_db, DatabaseSession
from database.models import (WordTranslation, WordEn, WordUa, WordTranslationKnowledge as Knowledge,
                             LastWordTranslationRequest, User)
from endpoints.user.tools import validate_session

router = APIRouter()

class MaterialRequest(BaseModel):
    translate_from: Literal["en", "ua"] = Field(..., description="Language to translate from, either 'en' for English or 'ua' for Ukrainian")

class WordMaterialResponse(BaseModel):
    word: str = Field(..., description="Word to translate")

@router.get("/random-word", response_model=WordMaterialResponse)
async def random_word(translate_from: Literal["en", "ua"], user: User = Depends(validate_session), db = Depends(get_db)):
    '''
    This function returns a random word from database to translate.
    '''
    random_translation = db.query(WordTranslation).order_by(func.random()).first()
    word_knowledge = (db.query(Knowledge).
                      filter(Knowledge.word_translation_id == random_translation.id).first())
    if word_knowledge is None:
        word_knowledge = Knowledge(word_translation_id=random_translation.id, user_id=user.id, knowledge=0)
        db.add(word_knowledge)
        db.commit()
    else:
        word_knowledge.knowledge -= 10
    last_request = LastWordTranslationRequest(knowledge_id=word_knowledge.id, user_id=user.id)
    db.add(last_request)
    db.commit()

    return {"word": random_translation.word_en.word if translate_from == "en" else random_translation.word_ua.word}


class MaterialValidationRequest(BaseModel):
    translate_from: Literal["en", "ua"] = Field(..., description="Language to translate from, either 'en' for English or 'ua' for Ukrainian")
    word_original: str = Field(..., description="Word to translate")
    word_translated: str = Field(..., description="Word translated")

class TranslationValidationResponse(BaseModel):
    is_correct: bool = Field(..., description="Is the translation correct")
    possible_answers: List[str] = Field(..., description="Possible answers")

def possible_translations(word: str, translate_from: Literal["en", "ua"], db: DatabaseSession):
    if translate_from == "en":
        word_translations = db.query(WordTranslation).filter(WordTranslation.word_en.has(word=word)).order_by(func.random()).limit(5)
        return [word_translation.word_ua.word for word_translation in word_translations]
    else:
        word_translations = db.query(WordTranslation).filter(WordTranslation.word_ua.has(word=word)).order_by(func.random()).limit(5)
        return [word_translation.word_en.word for word_translation in word_translations]

def word_incorrect(user: User):
    db = next(get_db())
    last_request = db.query(LastWordTranslationRequest).filter(LastWordTranslationRequest.user_id == user.id).first()
    knowledge = last_request.knowledge
    knowledge.knowledge = max(0, knowledge.knowledge - 10)
    db.commit()

@router.post("/random-word", response_model=TranslationValidationResponse)
async def random_word_validation(request: MaterialValidationRequest, user: User = Depends(validate_session),
                                 db: DatabaseSession = Depends(get_db)):
    '''
    This function validates a random word from database to translate.
    '''
    last_request = db.query(LastWordTranslationRequest).filter(LastWordTranslationRequest.user_id == user.id).first()
    if last_request is None:
        raise HTTPException(status_code=400, detail="Bad Request (no translation was requested)")
    if request.translate_from == "en":
        word_en = db.query(WordEn).filter(WordEn.word == request.word_original).first()
        word_ua = db.query(WordUa).filter(WordUa.word == request.word_translated).first()
    else:
        word_en = db.query(WordEn).filter(WordEn.word == request.word_translated).first()
        word_ua = db.query(WordUa).filter(WordUa.word == request.word_original).first()
    if (request.translate_from == "en" and word_en is None) or (request.translate_from == "ua" and word_ua is None):
        raise HTTPException(status_code=400, detail="Bad Request (original word is wrong)")
    possible_answers = possible_translations(request.word_original, request.translate_from, db)
    if request.translate_from == "en" and word_ua is None:
        word_incorrect(user)
        response = TranslationValidationResponse(is_correct=False, possible_answers=possible_answers)
        db.delete(last_request)
        db.commit()
        return response
    elif word_ua is None:
        word_incorrect(user)
        response = TranslationValidationResponse(is_correct=False, possible_answers=possible_answers)
        db.delete(last_request)
        db.commit()
        return response
    word_translation = db.query(WordTranslation).filter(WordTranslation.word_en.has(word=request.word_original),
                                                        WordTranslation.word_ua.has(word=request.word_translated)).first()
    if word_translation is None:
        word_incorrect(user)
        response = TranslationValidationResponse(is_correct=False, possible_answers=possible_answers)
        db.delete(last_request)
        db.commit()
        return response

    knowledge = last_request.knowledge
    knowledge.knowledge = min(100, knowledge.knowledge + 10)
    knowledge_added = (db.query(Knowledge).
                       filter(Knowledge.word_translation_id == word_translation.id and Knowledge.user_id == user.id)
                       .first())
    if knowledge_added is None:
        knowledge_added = Knowledge(word_translation_id=word_translation.id, user_id=user.id)
        db.add(knowledge_added)
    knowledge_added.knowledge = min(100, knowledge_added.knowledge + 10)
    db.commit()
    response = TranslationValidationResponse(is_correct=True, possible_answers=possible_answers)
    db.delete(last_request)
    db.commit()
    return response
