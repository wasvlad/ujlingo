import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
import jwt
from sqlalchemy.orm import Session

from database import get_db
from database.models import User
from .hashing import hash_password, verify_password
from .tools import is_strong_password, generate_token
from endpoints.tools import MessageResponse, ErrorResponse
from notifications.email import EmailNotificationService

router = APIRouter()

class PasswordResetRequest(BaseModel):
    email: EmailStr

@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(data: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Send email with link for password reset.
    """
    existing_user = db.query(User).filter(User.email == data.email).first()
    if not existing_user:
        return {"message": "A password reset link has been sent."}

    token = generate_token(str(data.email), os.getenv("PASSWORD_RESET_KEY"))

    front_end_url = os.getenv("FRONTEND_URL")

    email_service = EmailNotificationService(existing_user)
    email_service.send_notification("Password reset request",
                                    f"To reset your password, click here: {front_end_url}/html/reset-password.html?token={token}")

    return {"message": "A password reset link has been sent."}

class ResetPassword(BaseModel):
    password: str = Field(..., min_length=8, max_length=50)

@router.post("/reset-password", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request (Token expired, Invalid token, Weak password)"},
    404: {"model": ErrorResponse, "description": "Not Found (User not found)"}
})
async def reset_password(token: str, data: ResetPassword , db: Session = Depends(get_db)):
    """
    Resets the password for the user. The token is sent to the email.
    """
    secret_key = os.getenv("PASSWORD_RESET_KEY")

    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = db.query(User).filter(User.email == payload["email"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_password(data.password, str(user.password_hash)):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")

    if not is_strong_password(data.password):
        raise HTTPException(status_code=400, detail="Password is weak")

    user.password_hash = hash_password(data.password)
    db.commit()

    return {"message": "Password reset successfully"}