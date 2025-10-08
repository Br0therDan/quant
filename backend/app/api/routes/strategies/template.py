"""
Template API Routes
"""

from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError

from mysingle_quant.auth import (
    get_current_active_verified_user,
    get_current_active_superuser,
    User,
)
from app.models.strategy import StrategyType
from app.schemas.strategy import (
    StrategyCreateFromTemplate,
    StrategyResponse,
    TemplateCreate,
    TemplateListResponse,
    TemplateResponse,
    TemplateUpdate,
)
from app.services.service_factory import service_factory
from app.services.strategy_service import StrategyService

router = APIRouter(dependencies=[Depends(get_current_active_verified_user)])


async def get_strategy_service() -> AsyncGenerator[StrategyService, None]:
    """Dependency to get strategy service with proper cleanup"""
    service = service_factory.get_strategy_service()
    try:
        yield service
    finally:
        pass  # ServiceFactory manages cleanup


@router.post(
    "/",
    response_model=TemplateResponse,
    dependencies=[Depends(get_current_active_superuser)],
)
async def create_template(
    request: TemplateCreate,
    service: StrategyService = Depends(get_strategy_service),
):
    """Create a new strategy template (Superuser only)"""
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
            parameter_schema=template.parameter_schema or {},
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at,
            tags=template.tags,
        )

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"검증 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 생성 실패: {str(e)}")


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
                parameter_schema=template.parameter_schema or {},
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
        raise HTTPException(status_code=500, detail=f"템플릿 조회 실패: {str(e)}")


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    service: StrategyService = Depends(get_strategy_service),
):
    """Get template by ID"""
    try:
        template = await service.get_template_by_id(template_id)
        if not template:
            raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            strategy_type=template.strategy_type,
            description=template.description,
            default_parameters=template.default_parameters,
            parameter_schema=template.parameter_schema or {},
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at,
            tags=template.tags,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 조회 실패: {str(e)}")


@router.patch(
    "/{template_id}",
    response_model=TemplateResponse,
    dependencies=[Depends(get_current_active_superuser)],
)
async def update_template(
    template_id: str,
    request: TemplateUpdate,
    service: StrategyService = Depends(get_strategy_service),
):
    """Update template by ID (Superuser only)"""
    try:
        template = await service.update_template(
            template_id=template_id,
            name=request.name,
            description=request.description,
            default_parameters=request.default_parameters,
            parameter_schema=request.parameter_schema,
            tags=request.tags,
        )

        if not template:
            raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            strategy_type=template.strategy_type,
            description=template.description,
            default_parameters=template.default_parameters,
            parameter_schema=template.parameter_schema or {},
            usage_count=template.usage_count,
            created_at=template.created_at,
            updated_at=template.updated_at,
            tags=template.tags,
        )

    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"검증 오류: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 업데이트 실패: {str(e)}")


@router.delete("/{template_id}", dependencies=[Depends(get_current_active_superuser)])
async def delete_template(
    template_id: str,
    service: StrategyService = Depends(get_strategy_service),
):
    """Delete template by ID (Superuser only)"""
    try:
        success = await service.delete_template(template_id)
        if not success:
            raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

        return {
            "message": "템플릿이 성공적으로 삭제되었습니다",
            "template_id": template_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 삭제 실패: {str(e)}")


@router.post("/{template_id}/create-strategy", response_model=StrategyResponse)
async def create_strategy_from_template(
    template_id: str,
    request: StrategyCreateFromTemplate,
    current_user: User = Depends(get_current_active_verified_user),
    service: StrategyService = Depends(get_strategy_service),
):
    """Create a strategy instance from template"""
    try:
        strategy = await service.create_strategy_from_template(
            template_id=template_id,
            name=request.name,
            parameter_overrides=request.parameter_overrides,
            user_id=str(current_user.id),
        )

        if not strategy:
            raise HTTPException(status_code=404, detail="템플릿을 찾을 수 없습니다")

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
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=f"매개변수 검증 실패: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"전략 생성 실패: {str(e)}")


@router.get("/analytics/usage-stats")
async def get_template_usage_stats(
    service: StrategyService = Depends(get_strategy_service),
):
    """Get template usage statistics"""
    try:
        templates = await service.get_templates()

        # 사용량 통계 계산
        total_templates = len(templates)
        total_usage = sum(template.usage_count for template in templates)

        # 전략 타입별 분포
        type_distribution = {}
        for template in templates:
            strategy_type = template.strategy_type.value
            if strategy_type not in type_distribution:
                type_distribution[strategy_type] = {"count": 0, "usage": 0}
            type_distribution[strategy_type]["count"] += 1
            type_distribution[strategy_type]["usage"] += template.usage_count

        # 인기 템플릿 (사용량 상위 5개)
        popular_templates = sorted(
            templates, key=lambda x: x.usage_count, reverse=True
        )[:5]

        popular_list = [
            {
                "id": str(template.id),
                "name": template.name,
                "strategy_type": template.strategy_type.value,
                "usage_count": template.usage_count,
            }
            for template in popular_templates
        ]

        return {
            "status": "success",
            "statistics": {
                "total_templates": total_templates,
                "total_usage": total_usage,
                "average_usage": (
                    total_usage / total_templates if total_templates > 0 else 0
                ),
                "type_distribution": type_distribution,
                "popular_templates": popular_list,
            },
            "analyzed_at": "2024-09-29T00:00:00Z",  # 현재 시간으로 설정
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"템플릿 통계 조회 실패: {str(e)}")
