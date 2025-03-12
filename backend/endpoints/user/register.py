import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
import jwt
from sqlalchemy.orm import Session

from database import get_db
from database.models import User
from .hashing import hash_password
from email_service import write_email
from .tools import is_strong_password, generate_token, ErrorResponse

router = APIRouter()

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=50)
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)


class MessageResponse(BaseModel):
    message: str

@router.post("/register", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request (existing user, weak password)"},
})
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. Email should be confirmed by clicking on a link sent to the email.
    """
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if not is_strong_password(user.password):
        raise HTTPException(status_code=400, detail="Password is not strong enough")

    hashed_password = hash_password(user.password)

    new_user = User(
        email=str(user.email),
        password_hash=hashed_password,
        name=user.name,
        surname=user.surname
    )
    db.add(new_user)

    token = generate_token(str(user.email), os.getenv("SECRET_KEY"))

    front_end_url = os.getenv("FRONTEND_URL")

    write_email(str(user.email), "Confirm your email", f"To confirm your email, click here: {front_end_url}/user/confirm_email?token={token}")

    db.commit()

    return {"message": "User registered successfully"}


@router.get("/confirm_email", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request (Token expired, Invalid token)"},
    404: {"model": ErrorResponse, "description": "Not Found (User not found)"}
})
async def confirm_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm user's email.
    """
    secret_key = os.getenv("SECRET_KEY")

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == payload["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_confirmed = True
    db.commit()

    return {"message": "Email confirmed successfully"}