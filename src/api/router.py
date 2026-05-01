from fastapi import APIRouter
from src.api import cases, flags, scores

router = APIRouter()

router.include_router(cases.router)
router.include_router(flags.router)
router.include_router(scores.router)
