from fastapi import APIRouter, Depends, HTTPException

from database.models import User
from endpoints.tools import MessageResponse, ErrorResponse
from endpoints.user.tools import validate_session
from test_system.builder.test import TestBuilder
from test_system.caching import RedisCaching, RedisCachingException as CachingException

router = APIRouter()

@router.post("/new", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test_new_sentences(user: User = Depends(validate_session)):
    """Initialize a test session with new sentences."""
    try:
        builder = TestBuilder(user)
        builder.add_new_sentences(10)
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")

@router.post("/weak-knowledge", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test_weak_sentences(user: User = Depends(validate_session)):
    """Initialize a test session with sentences with weak knowledge."""
    try:
        builder = TestBuilder(user)
        builder.add_weak_sentences()
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")

@router.post("/strong-knowledge", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test_strong_sentences(user: User = Depends(validate_session)):
    """Initialize a test session with sentences with strong knowledge."""
    try:
        builder = TestBuilder(user)
        builder.add_strong_knowledge_sentences()
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")
