from fastapi import APIRouter
from . import data_migration

router = APIRouter()
router.include_router(data_migration.router)
