"""Routes exposing GenAI model catalogue and policies."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.gen_ai.models import (
    ModelConfigResponse,
    ModelListResponse,
    ServiceModelPolicyResponse,
)
from app.services.gen_ai.core.openai_client_manager import (
    InvalidModelError,
    ModelTier,
)
from app.services.service_factory import service_factory

router = APIRouter()


@router.get("", response_model=ModelListResponse)
async def list_models(tier: Optional[ModelTier] = Query(None, description="필터할 모델 티어")) -> ModelListResponse:
    """Return all configured OpenAI models, optionally filtered by tier."""

    manager = service_factory.get_openai_client_manager()
    models = manager.list_models(tier=tier)
    return ModelListResponse(
        models=[ModelConfigResponse.from_config(model) for model in models],
        total=len(models),
    )


@router.get("/{service_name}", response_model=ServiceModelPolicyResponse)
async def get_service_models(service_name: str) -> ServiceModelPolicyResponse:
    """Return policy and allowed models for a given GenAI service."""

    manager = service_factory.get_openai_client_manager()
    try:
        policy = manager.get_service_policy(service_name)
        models = manager.list_models_for_service(service_name)
    except InvalidModelError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ServiceModelPolicyResponse(
        service_name=policy.service_name,
        default_model=policy.default_model,
        allowed_tiers=policy.allowed_tiers,
        required_capabilities=policy.required_capabilities,
        models=[ModelConfigResponse.from_config(model) for model in models],
    )
