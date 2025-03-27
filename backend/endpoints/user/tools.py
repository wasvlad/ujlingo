import os
import re
from datetime import datetime, timezone, timedelta
from typing import Type

import jwt
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session as DatabaseSession

from database import get_db
from database.models import Session, User


def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def generate_token(email: str,
                         secret_key: str,
                         expiration_date: datetime = datetime.now(timezone.utc) + timedelta(minutes=5)) -> str:
    token = jwt.encode({"email": email, "exp": expiration_date},
                          secret_key, algorithm="HS256")
    return token


def validate_session(request: Request, db: DatabaseSession = Depends(get_db)) -> Type[User]:
    secret_key = os.getenv("SECRET_KEY")
    access_token = request.cookies.get("session-token")

    if not access_token:
        raise HTTPException(status_code=401, detail="Login required")

    try:
        jwt.decode(access_token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    session = db.query(Session).filter(Session.token == access_token).first()
    if not session.is_active:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")
    if not user.is_confirmed:
        raise HTTPException(status_code=403, detail="Email is not confirmed")

    return user