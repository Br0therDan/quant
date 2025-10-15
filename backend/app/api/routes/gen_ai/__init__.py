"""
Gen AI domain API routes
"""
from fastapi import APIRouter
from .chatops import router as chatops_router
from .chatops_advanced import router as chatops_advanced_router
from .narrative import router as narrative_router
from .prompt_governance import router as prompt_governance_router
from .strategy_builder import router as strategy_builder_router


router = APIRouter()

router.include_router(chatops_router, prefix="/chatops")
router.include_router(chatops_advanced_router, prefix="/chatops-advanced")
router.include_router(narrative_router, prefix="/narrative")
router.include_router(prompt_governance_router, prefix="/prompt-governance")
router.include_router(strategy_builder_router, prefix="/strategy-builder")
