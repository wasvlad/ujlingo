import pickle

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing_extensions import Buffer

from database.models import User
from endpoints.user.tools import validate_session
from endpoints.tools import MessageResponse, ErrorResponse
from test_system.caching import init_redis
from test_system.random.words import WordTranslationsTestBuilder as TestBuilder
from test_system.main import QuestionJsonBase, Test, Result, NoQuestionsException

router = APIRouter()

@router.post("/init_test", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test(user: User = Depends(validate_session)):
    r = init_redis()
    res = r.get(f"user:{user.id}:test")
    if res is not None:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    test = TestBuilder.build(user)
    res = r.setex(f"user:{user.id}:test", 3600, pickle.dumps(test))
    return MessageResponse(message="Test session initialized")


@router.get("/get_question", response_model=QuestionJsonBase | MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is not initialized"},
    200: {"description": "Current question or message that test is finished"}
})
async def get_question(user: User = Depends(validate_session)):
    r = init_redis()
    test: Buffer = r.get(f"user:{user.id}:test")
    if test is None:
        raise HTTPException(status_code=400, detail="Test session is not initialized")
    test: Test = pickle.loads(test)
    question = test.get_question()
    if question is None:
        res = r.delete(f"user:{user.id}:test")
        return MessageResponse(message="Test is finished")
    return question


class AnswerQuestion(BaseModel):
    answer: str = Field(..., description="Answer to the question")


@router.post("/answer_question", response_model=Result, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is not initialized"}
})
async def answer_question(data: AnswerQuestion, user: User = Depends(validate_session)):
    r = init_redis()
    test: Buffer = r.get(f"user:{user.id}:test")
    if test is None:
        raise HTTPException(status_code=400, detail="Test session is not initialized")
    test: Test = pickle.loads(test)
    try:
        answer = test.give_answer(data.answer)
        res = r.setex(f"user:{user.id}:test", 3600, pickle.dumps(test))
    except NoQuestionsException:
        res = r.delete(f"user:{user.id}:test")
        raise HTTPException(status_code=400, detail="Test is finished")
    return answer