from fastapi import APIRouter, Depends

from database.models import User
from .tools import validate_admin_session
from ..tools import ErrorResponse, MessageResponse

router = APIRouter()

@router.get("/validate-session", response_model=MessageResponse, responses={
    401: {"model": ErrorResponse, "description": "Unauthorized"},
    403: {"model": ErrorResponse, "description": "Forbidden"},
    404: {"model": ErrorResponse, "description": "Not Found (user was deleted)"}
})
async def login_user(user: User = Depends(validate_admin_session)):
    '''
    This endpoint validates is the user is logged in
    '''
    return {"message": f"Hello {user.name}!"}