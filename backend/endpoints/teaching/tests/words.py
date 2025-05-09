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
async def init_test_new_words(user: User = Depends(validate_session)):
    """Initialize a test session with new words."""
    try:
        builder = TestBuilder(user)
        builder.add_new_words(10)
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")

@router.post("/weak-knowledge", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test_weak_knowledge_words(user: User = Depends(validate_session)):
    """Init test with weak knowledge words"""
    try:
        builder = TestBuilder(user)
        builder.add_weak_knowledge_words(10)
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")

@router.post("/strong-knowledge", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request: Test session is already initialized"}
})
async def init_test_strong_knowledge_words(user: User = Depends(validate_session)):
    """Init test with strong knowledge words (to revise them)"""
    try:
        builder = TestBuilder(user)
        builder.add_strong_knowledge_words(10)
        builder.build(caching_class=RedisCaching)
    except CachingException:
        raise HTTPException(status_code=400, detail="Test session is already initialized")
    return MessageResponse(message="Test session initialized")
