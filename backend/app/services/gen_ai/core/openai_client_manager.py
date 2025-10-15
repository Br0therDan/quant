"""Centralized OpenAI client and model policy manager."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Iterable, List, Optional

import structlog
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ModelTier(str, Enum):
    """Pricing/quality tier of an OpenAI model."""

    MINI = "mini"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"


class ModelCapability(str, Enum):
    """Capabilities supported by an OpenAI model."""

    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    REASONING = "reasoning"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"


class ModelConfig(BaseModel):
    """Configuration metadata for a single OpenAI model."""

    model_id: str = Field(..., description="OpenAI model identifier")
    tier: ModelTier = Field(..., description="Pricing tier")
    capabilities: List[ModelCapability] = Field(
        ..., description="Supported model capabilities"
    )
    input_price_per_1m: float = Field(
        ..., description="Input token price per 1M tokens in USD"
    )
    output_price_per_1m: float = Field(
        ..., description="Output token price per 1M tokens in USD"
    )
    max_tokens: int = Field(..., description="Maximum tokens supported by the model")
    supports_rag: bool = Field(..., description="Whether the model is optimised for RAG")
    description: str = Field(..., description="Human readable description")


class ServiceModelPolicy(BaseModel):
    """Allowed model configuration for a specific GenAI service."""

    service_name: str = Field(..., description="Service identifier")
    allowed_tiers: List[ModelTier] = Field(
        ..., description="Model tiers that can be used by the service"
    )
    default_model: str = Field(..., description="Default model id for the service")
    required_capabilities: List[ModelCapability] = Field(
        default_factory=list, description="Capabilities required by the service"
    )


class ModelUsageRecord(BaseModel):
    """Usage record captured for token cost tracking."""

    service_name: str
    model_id: str
    input_tokens: int
    output_tokens: int
    total_cost_usd: float


class InvalidModelError(ValueError):
    """Raised when a model is not allowed for a service."""


_MODEL_CATALOG: Dict[str, ModelConfig] = {
    "gpt-4o-mini": ModelConfig(
        model_id="gpt-4o-mini",
        tier=ModelTier.MINI,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=0.15,
        output_price_per_1m=0.60,
        max_tokens=128_000,
        supports_rag=True,
        description="Cost-efficient GPT-4o distilled model ideal for interactive tooling.",
    ),
    "gpt-4o": ModelConfig(
        model_id="gpt-4o",
        tier=ModelTier.STANDARD,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=2.50,
        output_price_per_1m=10.00,
        max_tokens=128_000,
        supports_rag=True,
        description="General purpose GPT-4o model balancing quality and latency.",
    ),
    "gpt-4-turbo": ModelConfig(
        model_id="gpt-4-turbo",
        tier=ModelTier.ADVANCED,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
            ModelCapability.CODE_GENERATION,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=10.00,
        output_price_per_1m=30.00,
        max_tokens=128_000,
        supports_rag=False,
        description="High capacity GPT-4 Turbo model for complex reasoning workloads.",
    ),
    "o1-preview": ModelConfig(
        model_id="o1-preview",
        tier=ModelTier.PREMIUM,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        ],
        input_price_per_1m=15.00,
        output_price_per_1m=60.00,
        max_tokens=32_000,
        supports_rag=False,
        description="Reasoning-optimised preview model for complex analysis tasks.",
    ),
}

_SERVICE_POLICIES: Dict[str, ServiceModelPolicy] = {
    "strategy_builder": ServiceModelPolicy(
        service_name="strategy_builder",
        allowed_tiers=[ModelTier.MINI, ModelTier.STANDARD],
        default_model="gpt-4o-mini",
        required_capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.ANALYSIS,
        ],
    ),
    "narrative_report": ServiceModelPolicy(
        service_name="narrative_report",
        allowed_tiers=[ModelTier.STANDARD, ModelTier.ADVANCED, ModelTier.PREMIUM],
        default_model="gpt-4o",
        required_capabilities=[ModelCapability.CHAT, ModelCapability.ANALYSIS],
    ),
    "chatops_advanced": ServiceModelPolicy(
        service_name="chatops_advanced",
        allowed_tiers=[ModelTier.STANDARD, ModelTier.ADVANCED, ModelTier.PREMIUM],
        default_model="gpt-4o",
        required_capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
            ModelCapability.FUNCTION_CALLING,
        ],
    ),
}


class OpenAIClientManager:
    """Singleton that centralises OpenAI client access and policy validation."""

    _instance: Optional["OpenAIClientManager"] = None
    _client: Optional[AsyncOpenAI] = None

    def __new__(cls) -> "OpenAIClientManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialised") and self._initialised:
            return

        self._api_key = settings.OPENAI_API_KEY
        self._model_catalog = dict(_MODEL_CATALOG)
        self._service_policies = dict(_SERVICE_POLICIES)
        self._initialised = True

    @classmethod
    def _reset_instance(cls) -> None:
        """Reset singleton state (useful for tests)."""

        cls._instance = None
        cls._client = None

    def get_client(self) -> AsyncOpenAI:
        """Return a lazily initialised AsyncOpenAI client."""

        if self._client is not None:
            return self._client

        if not self._api_key or self._api_key == "your-openai-api-key":
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. Set a valid key before using OpenAI services."
            )

        self._client = AsyncOpenAI(api_key=self._api_key)
        logger.info("openai_client_initialised")
        return self._client

    def get_model_config(self, model_id: str) -> ModelConfig:
        """Return the configuration for a given model id."""

        try:
            return self._model_catalog[model_id]
        except KeyError as exc:
            raise InvalidModelError(f"Unknown OpenAI model: {model_id}") from exc

    def get_service_policy(self, service_name: str) -> ServiceModelPolicy:
        """Return the policy definition for a given service."""

        try:
            return self._service_policies[service_name]
        except KeyError as exc:
            raise InvalidModelError(f"Unknown service policy: {service_name}") from exc

    def list_models(self, tier: Optional[ModelTier] = None) -> List[ModelConfig]:
        """Return all configured models, optionally filtered by tier."""

        models = list(self._model_catalog.values())
        if tier:
            models = [model for model in models if model.tier == tier]
        return models

    def list_models_for_service(self, service_name: str) -> List[ModelConfig]:
        """Return models that satisfy the service policy."""

        policy = self.get_service_policy(service_name)
        return [
            model
            for model in self._model_catalog.values()
            if model.tier in policy.allowed_tiers
            and self._has_capabilities(model.capabilities, policy.required_capabilities)
        ]

    def validate_model_for_service(
        self, service_name: str, model_id: Optional[str]
    ) -> ModelConfig:
        """Validate the requested model for a service, returning the resolved config."""

        policy = self.get_service_policy(service_name)
        resolved_model_id = model_id or policy.default_model
        model_config = self.get_model_config(resolved_model_id)

        if model_config.tier not in policy.allowed_tiers:
            raise InvalidModelError(
                f"Model {resolved_model_id} (tier={model_config.tier.value}) is not allowed for service {service_name}."
            )

        if not self._has_capabilities(
            model_config.capabilities, policy.required_capabilities
        ):
            raise InvalidModelError(
                f"Model {resolved_model_id} does not provide required capabilities for service {service_name}."
            )

        return model_config

    def track_usage(
        self, service_name: str, model_id: str, usage: Any | None
    ) -> Optional[ModelUsageRecord]:
        """Track token usage for a given service/model combination."""

        if usage is None:
            return None

        prompt_tokens = self._extract_usage_value(usage, ["prompt_tokens", "input_tokens"])
        completion_tokens = self._extract_usage_value(
            usage, ["completion_tokens", "output_tokens"]
        )

        if prompt_tokens is None and completion_tokens is None:
            return None

        prompt_tokens = prompt_tokens or 0
        completion_tokens = completion_tokens or 0

        model_config = self.get_model_config(model_id)
        cost = (
            (prompt_tokens / 1_000_000) * model_config.input_price_per_1m
            + (completion_tokens / 1_000_000) * model_config.output_price_per_1m
        )

        record = ModelUsageRecord(
            service_name=service_name,
            model_id=model_id,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            total_cost_usd=round(cost, 6),
        )

        logger.info(
            "openai_usage_tracked",
            service=service_name,
            model=model_id,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            total_cost_usd=record.total_cost_usd,
        )
        return record

    @staticmethod
    def _has_capabilities(
        model_capabilities: Iterable[ModelCapability],
        required_capabilities: Iterable[ModelCapability],
    ) -> bool:
        capabilities = set(model_capabilities)
        return all(capability in capabilities for capability in required_capabilities)

    @staticmethod
    def _extract_usage_value(usage: Any, keys: Iterable[str]) -> Optional[int]:
        for key in keys:
            if hasattr(usage, key):
                value = getattr(usage, key)
                if isinstance(value, int):
                    return value
            if isinstance(usage, dict) and key in usage:
                value = usage[key]
                if isinstance(value, int):
                    return value
        return None
