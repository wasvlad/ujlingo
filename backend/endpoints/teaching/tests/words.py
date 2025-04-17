from fastapi import APIRouter, Depends, HTTPException

from database.models import User
from endpoints.tools import MessageResponse, ErrorResponse
from endpoints.user.tools import validate_session
from test_system.builder.test import NewWordsTestBuilder
from test_system.caching import RedisCaching, RedisCachingException as CachingException

router = APIRouter()

@router.post("/new", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test_new_words(user: User = Depends(validate_session)):
    try:
        NewWordsTestBuilder.build(user, caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")
