"""
Template API Routes
"""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query

from app.models.strategy import StrategyType
from app.schemas.strategy import (
    StrategyFromTemplateRequest,
    StrategyResponse,
    TemplateCreateRequest,
    TemplateListResponse,
    TemplateResponse,
)
from app.services.strategy_service import StrategyService

router = APIRouter(prefix="/templates", tags=["Templates"])


async def get_strategy_service() -> AsyncGenerator[StrategyService, None]:
    """Dependency to get strategy service with proper cleanup"""
    service = StrategyService()
    try:
        yield service
    finally:
        pass  # No cleanup needed for this service


@router.post("/", response_model=TemplateResponse)
async def create_template(
    request: TemplateCreateRequest,
    service: StrategyService = Depends(get_strategy_service),
):
    """Create a new strategy template"""
    try:
        template = await service.create_template(
            name=request.name,
            strategy_type=request.strategy_type,
            description=request.description,
            default_parameters=request.default_parameters,
            parameter_schema=request.parameter_schema,
            tags=request.tags,
        )

        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            strategy_type=template.strategy_type,
            description=template.description,
            default_parameters=template.default_parameters,
            parameter_schema=template.parameter_schema,
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at,
            tags=template.tags,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=TemplateListResponse)
async def get_templates(
    strategy_type: StrategyType | None = Query(None, description="전략 타입 필터"),
    service: StrategyService = Depends(get_strategy_service),
):
    """Get list of strategy templates"""
    try:
        templates = await service.get_templates(strategy_type=strategy_type)

        template_responses = [
            TemplateResponse(
                id=str(template.id),
                name=template.name,
                strategy_type=template.strategy_type,
                description=template.description,
                default_parameters=template.default_parameters,
                parameter_schema=template.parameter_schema,
                usage_count=template.usage_count,
                created_at=template.created_at,
                updated_at=template.updated_at,
                tags=template.tags,
            )
            for template in templates
        ]

        return TemplateListResponse(
            templates=template_responses,
            total=len(template_responses),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{template_id}/create-strategy", response_model=StrategyResponse)
async def create_strategy_from_template(
    template_id: str,
    request: StrategyFromTemplateRequest,
    service: StrategyService = Depends(get_strategy_service),
):
    """Create a strategy instance from template"""
    try:
        strategy = await service.create_strategy_from_template(
            template_id=template_id,
            name=request.name,
            parameter_overrides=request.parameter_overrides,
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="Template not found")

        return StrategyResponse(
            id=str(strategy.id),
            name=strategy.name,
            strategy_type=strategy.strategy_type,
            description=strategy.description,
            parameters=strategy.parameters,
            is_active=strategy.is_active,
            is_template=strategy.is_template,
            created_by=strategy.created_by,
            created_at=strategy.created_at,
            updated_at=strategy.updated_at,
            tags=strategy.tags,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
