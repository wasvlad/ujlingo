from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database.models import User
from test_system.caching import RedisCaching, RedisCachingException as CachingException
from test_system.main import QuestionJsonBase, Test, Result, NoQuestionsException
from test_system.sentences import ReorderQuestionJson
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
