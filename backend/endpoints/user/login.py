from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import os

from database import get_db
from database.models import User, Session as UserSession
from .hashing import verify_password
from .tools import generate_token
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
    This function logs in a user, if login is successful, it returns an access token.
    '''
    existing_user: User | None = db.query(User).filter(User.email == user.email).first()
    if existing_user is None:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, existing_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = generate_token(str(user.email), os.getenv("SECRET_KEY"),
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