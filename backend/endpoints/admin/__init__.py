from fastapi import APIRouter
from . import data_migration
from . import session

router = APIRouter()
router.include_router(data_migration.router)
router.include_router(session.router)
