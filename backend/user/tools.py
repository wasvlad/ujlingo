import os
import re
from datetime import datetime, timezone, timedelta

import jwt


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