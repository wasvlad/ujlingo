import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database.models import User, Sentence, SentenceTranslation
from test_system.builder.test import TestBuilder
from test_system.caching import RedisCaching, RedisCachingException as CachingException
from test_system.main import QuestionJsonBase, Test, Result, NoQuestionsException
from test_system.sentences import ReorderQuestionJson, ReorderTranslationQuestion
from test_system.words import MSQQuestionJson
from . import random, tests
from ..tools import MessageResponse, ErrorResponse
from ..user.tools import validate_session

router = APIRouter()
router.include_router(random.router, prefix="/random")
router.include_router(tests.router, prefix="/tests")


@router.get("/get_question", response_model=QuestionJsonBase | MSQQuestionJson | ReorderQuestionJson | MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is not initialized"},
    200: {"description": "Current question or message that test is finished"}
})
async def get_question(user: User = Depends(validate_session)):
    try:
        test = Test.load_from_cache(user, caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is not initialized")
    question = test.get_question()
    if question is None:
        return MessageResponse(message="Test is finished")
    return question


class AnswerQuestion(BaseModel):
    answer: str = Field(..., description="Answer to the question")


@router.post("/answer_question", response_model=Result, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is not initialized"}
})
async def answer_question(data: AnswerQuestion, user: User = Depends(validate_session)):
    try:
        test = Test.load_from_cache(user, caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is not initialized")
    try:
        answer = test.give_answer(data.answer)
    except NoQuestionsException:
        raise HTTPException(status_code=400, detail="Test is finished")
    return answer


class CustomSentenceTest(BaseModel):
    sentence: str = Field(..., description="Custom sentence in ukrainian")


@router.post("/custom_sentence_test", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def custom_sentence_test(data: CustomSentenceTest, user: User = Depends(validate_session)):
    uk_sentence = data.sentence
    url = os.getenv("TRANSLATOR_URL") + "/translate"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={"text": uk_sentence})
        response.raise_for_status()
        response_data = response.json()
    translation = response_data["translation"]
    sentence_uk_bd = Sentence(sentence=uk_sentence)
    sentence_tr_bd = Sentence(sentence=translation)
    translation = SentenceTranslation()
    translation.sentence_translated = sentence_tr_bd
    translation.sentence_original = sentence_uk_bd
    question = ReorderTranslationQuestion(translation=translation)
    try:
        builder = TestBuilder(user)
        builder.add_custom(question=question)
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")
