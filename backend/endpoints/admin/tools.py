from fastapi import HTTPException, Depends

from database.models import User
from ..user.tools import validate_session


def validate_admin_session(user: User = Depends(validate_session)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Access denied")

    return user