from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from database import get_db, DatabaseSession
from endpoints.tools import MessageResponse, ErrorResponse
from .hashing import verify_password, hash_password
from database.models import User
from .tools import validate_session, is_strong_password

router = APIRouter()

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/change-password", response_model=MessageResponse, responses={
    400: {"model": ErrorResponse, "description": "Bad Request (Invalid new password, Invalid old password)"},
})
async def password_change(data: PasswordChangeRequest, user: User = Depends(validate_session),
                          db: DatabaseSession = Depends(get_db)):
    '''
    This endpoint changes user password.
    '''
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid old password")

    if not is_strong_password(data.new_password):
        raise HTTPException(status_code=400, detail="New password is not strong enough")
    hashed_password = hash_password(data.new_password)
    user.password_hash = hashed_password
    db.commit()
    return MessageResponse(message="Password changed successfully")