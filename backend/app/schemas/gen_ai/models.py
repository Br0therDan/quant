"""Schemas for GenAI model catalogue and selection APIs."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.services.gen_ai.core.openai_client_manager import (
    ModelCapability,
    ModelConfig,
    ModelTier,
)


class ModelConfigResponse(BaseModel):
    """Public representation of a model configuration."""

    model_id: str = Field(..., description="OpenAI 모델 ID")
    tier: ModelTier = Field(..., description="모델 가격 티어")
    capabilities: List[ModelCapability] = Field(
        ..., description="지원되는 기능 (chat, analysis 등)"
    )
    input_price_per_1m: float = Field(
        ..., description="입력 토큰 100만개당 비용 (USD)"
    )
    output_price_per_1m: float = Field(
        ..., description="출력 토큰 100만개당 비용 (USD)"
    )
    max_tokens: int = Field(..., description="지원되는 최대 토큰 수")
    supports_rag: bool = Field(..., description="RAG 최적화 여부")
    description: str = Field(..., description="모델 설명")

    @classmethod
    def from_config(cls, config: ModelConfig) -> "ModelConfigResponse":
        """Create a response model from the internal configuration."""

        return cls(**config.model_dump())


class ModelListResponse(BaseModel):
    """Response payload for available models."""

    models: List[ModelConfigResponse] = Field(..., description="모델 목록")
    total: int = Field(..., description="총 모델 수")


class ServiceModelPolicyResponse(BaseModel):
    """Response describing service-specific policy and available models."""

    service_name: str = Field(..., description="서비스 이름")
    default_model: str = Field(..., description="기본 모델 ID")
    allowed_tiers: List[ModelTier] = Field(
        ..., description="허용된 모델 티어"
    )
    required_capabilities: List[ModelCapability] = Field(
        ..., description="필수 기능"
    )
    models: List[ModelConfigResponse] = Field(..., description="사용 가능한 모델 목록")


class ModelSelectionRequest(BaseModel):
    """Optional request payload for selecting a specific model."""

    model_id: Optional[str] = Field(
        default=None,
        description="사용할 모델 ID (미지정 시 기본값 사용)",
    )


__all__ = [
    "ModelConfigResponse",
    "ModelListResponse",
    "ServiceModelPolicyResponse",
    "ModelSelectionRequest",
]
