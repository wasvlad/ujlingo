from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import os

from database import get_db
from database.models import User, Session as UserSession
from .hashing import verify_password
from .tools import generate_token, validate_session
from ..tools import ErrorResponse, MessageResponse

router = APIRouter()

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str

@router.post("/login", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request (Invalid email or password)"}
})
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    '''
    This function logs in a user, if login is successful, it saves access token in http only cookies.
    After 200 response frontend can access protected endpoints without any additional actions.
    '''
    email = str(user.email).lower()
    existing_user: User | None = db.query(User).filter(User.email == email).first()
    if existing_user is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = generate_token(email, os.getenv("SECRET_KEY"),
                           expiration_date=datetime.now(timezone.utc) + timedelta(days=30))

    new_session = UserSession(
        token=token,
        user_id=existing_user.id,
        is_active=True
    )
    db.add(new_session)
    db.commit()

    response = JSONResponse(content={"message": "Login successful"})
    # samesite attribute helps protect against CSRF attacks.
    response.set_cookie(key="session-token", value=token, httponly=True, secure=True, samesite="lax")

    return response


@router.get("/validate-session", response_model=MessageResponse, responses={
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    403: {"model": ErrorResponse, "description": "Forbidden (required email confirmation or user is banned)"},
    404: {"model": ErrorResponse, "description": "Not Found (user was deleted)"}
})
async def login_user(user: User = Depends(validate_session)):
    '''
    This endpoint validates is the user is logged in
    '''
    return {"message": f"Hello {user.name}!"}

@router.get("/logout", response_model=MessageResponse)
async def logout(request: Request):
    '''
    This endpoint validates is the user is logged in
    '''
    response = JSONResponse(content={"message": "Logout successful"})
    for cookie in request.cookies:
        response.delete_cookie(key=cookie)
    return response
