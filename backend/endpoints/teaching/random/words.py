from fastapi import APIRouter, Depends, HTTPException

from database.models import User
from endpoints.user.tools import validate_session
from endpoints.tools import MessageResponse, ErrorResponse
from test_system.caching import RedisCaching, RedisCachingException as CachingException
from test_system.random.words import WordTranslationsTestBuilder as TestBuilder

router = APIRouter()

@router.post("/init_test", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test(user: User = Depends(validate_session)):
    try:
        TestBuilder.build(user, caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")
