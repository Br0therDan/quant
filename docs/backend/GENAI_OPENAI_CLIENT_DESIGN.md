# GenAI 도메인 OpenAI 클라이언트 리팩토링 설계

**작성일**: 2025-10-15  
**목적**: OpenAI 클라이언트 중앙화 + 모델 선택 + RAG 통합

---

## 📋 Executive Summary

### 현재 문제점

1. **중복 초기화**: 각 서비스마다 `AsyncOpenAI` 개별 생성 (3회 중복)
2. **하드코딩된 모델**: `gpt-4-turbo-preview`, `gpt-4o` 등 서비스마다 다름
3. **비용 최적화 부재**: 모든 요청이 고가 모델 사용 (gpt-4 계열)
4. **RAG 미구현**: 사용자 데이터 컨텍스트 활용 불가
5. **모델 선택 불가**: 사용자가 목적에 맞는 모델 선택 불가능

### 개선 방안 요약

1. ✅ **중앙화된 OpenAI Client Manager** 생성
2. ✅ **모델 카탈로그** (목적별 최적 모델 + 가격)
3. ✅ **사용자 모델 선택 API** (서비스별 허용 범위 제한)
4. ✅ **RAG Integration** (벡터 DB + 사용자 데이터 검색)
5. ✅ **토큰 사용량 추적** (비용 모니터링)

---

## 🏗️ 아키텍처 설계

### 1. OpenAI Client Manager (중앙화)

**위치**: `backend/app/services/gen_ai/core/openai_client_manager.py`

```python
"""
OpenAI Client Manager

목적:
- OpenAI 클라이언트 싱글톤 관리
- 모델 카탈로그 및 선택 로직
- 토큰 사용량 추적
- RAG 컨텍스트 통합
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from pydantic import BaseModel


class ModelTier(str, Enum):
    """모델 등급 (가격 기준)"""
    MINI = "mini"           # 가장 저렴 (단순 작업)
    STANDARD = "standard"   # 중간 (일반 작업)
    ADVANCED = "advanced"   # 고급 (복잡한 작업)
    PREMIUM = "premium"     # 최고급 (최고 성능)


class ModelCapability(str, Enum):
    """모델 기능"""
    CHAT = "chat"                    # 일반 대화
    CODE_GENERATION = "code_gen"     # 코드 생성
    ANALYSIS = "analysis"            # 데이터 분석
    REASONING = "reasoning"          # 복잡한 추론
    VISION = "vision"                # 이미지 분석
    FUNCTION_CALLING = "function"    # Function Calling


class ModelConfig(BaseModel):
    """모델 설정"""
    model_id: str                    # 모델 ID (예: "gpt-4o-mini")
    tier: ModelTier                  # 가격 등급
    capabilities: List[ModelCapability]  # 지원 기능
    input_price_per_1m: float        # 입력 100만 토큰당 가격 (USD)
    output_price_per_1m: float       # 출력 100만 토큰당 가격 (USD)
    max_tokens: int                  # 최대 토큰 수
    supports_rag: bool               # RAG 지원 여부
    description: str                 # 모델 설명


# 모델 카탈로그 (2025년 10월 기준 OpenAI 가격)
MODEL_CATALOG: Dict[str, ModelConfig] = {
    # Mini 등급 (저렴, 단순 작업)
    "gpt-4o-mini": ModelConfig(
        model_id="gpt-4o-mini",
        tier=ModelTier.MINI,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.ANALYSIS,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=0.15,   # $0.15 / 1M tokens
        output_price_per_1m=0.60,  # $0.60 / 1M tokens
        max_tokens=16_384,
        supports_rag=True,
        description="가장 저렴한 GPT-4o 계열. 단순 대화, 요약, 분류에 최적",
    ),

    # Standard 등급 (중간 가격, 일반 작업)
    "gpt-4o": ModelConfig(
        model_id="gpt-4o",
        tier=ModelTier.STANDARD,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=2.50,   # $2.50 / 1M tokens
        output_price_per_1m=10.00, # $10.00 / 1M tokens
        max_tokens=16_384,
        supports_rag=True,
        description="균형 잡힌 성능. 대부분의 작업에 적합",
    ),

    # Advanced 등급 (고가, 복잡한 작업)
    "gpt-4-turbo": ModelConfig(
        model_id="gpt-4-turbo",
        tier=ModelTier.ADVANCED,
        capabilities=[
            ModelCapability.CHAT,
            ModelCapability.CODE_GENERATION,
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING,
            ModelCapability.VISION,
            ModelCapability.FUNCTION_CALLING,
        ],
        input_price_per_1m=10.00,  # $10.00 / 1M tokens
        output_price_per_1m=30.00, # $30.00 / 1M tokens
        max_tokens=128_000,
        supports_rag=True,
        description="긴 컨텍스트 지원. 복잡한 분석, 긴 문서 처리",
    ),

    # Premium 등급 (최고가, 최고 성능)
    "o1-preview": ModelConfig(
        model_id="o1-preview",
        tier=ModelTier.PREMIUM,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.ANALYSIS,
        ],
        input_price_per_1m=15.00,  # $15.00 / 1M tokens
        output_price_per_1m=60.00, # $60.00 / 1M tokens
        max_tokens=128_000,
        supports_rag=True,
        description="최고 추론 능력. 복잡한 수학, 과학 문제 해결",
    ),
}


class ServiceModelPolicy(BaseModel):
    """서비스별 모델 선택 정책"""
    service_name: str
    allowed_tiers: List[ModelTier]     # 허용된 모델 등급
    default_model: str                 # 기본 모델
    required_capabilities: List[ModelCapability]  # 필수 기능


# 서비스별 모델 정책
SERVICE_MODEL_POLICIES: Dict[str, ServiceModelPolicy] = {
    "narrative_report": ServiceModelPolicy(
        service_name="narrative_report",
        allowed_tiers=[ModelTier.MINI, ModelTier.STANDARD],
        default_model="gpt-4o-mini",  # 리포트 생성은 저렴한 모델 충분
        required_capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
        ],
    ),
    "strategy_builder": ServiceModelPolicy(
        service_name="strategy_builder",
        allowed_tiers=[ModelTier.STANDARD, ModelTier.ADVANCED, ModelTier.PREMIUM],
        default_model="gpt-4o",  # 코드 생성은 중간 이상 모델 필요
        required_capabilities=[
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.FUNCTION_CALLING,
        ],
    ),
    "chatops_advanced": ServiceModelPolicy(
        service_name="chatops_advanced",
        allowed_tiers=[ModelTier.MINI, ModelTier.STANDARD],
        default_model="gpt-4o-mini",  # 일반 대화는 저렴한 모델 충분
        required_capabilities=[
            ModelCapability.CHAT,
            ModelCapability.FUNCTION_CALLING,
        ],
    ),
    "prompt_governance": ServiceModelPolicy(
        service_name="prompt_governance",
        allowed_tiers=[ModelTier.MINI],
        default_model="gpt-4o-mini",  # 정책 체크는 간단, 저렴한 모델로 충분
        required_capabilities=[
            ModelCapability.CHAT,
            ModelCapability.ANALYSIS,
        ],
    ),
}


class OpenAIClientManager:
    """OpenAI 클라이언트 매니저 (싱글톤)"""

    _instance: Optional["OpenAIClientManager"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            from app.core.config import settings

            api_key = settings.OPENAI_API_KEY
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")

            self.client = AsyncOpenAI(api_key=api_key)
            self.usage_tracker: Dict[str, Dict[str, int]] = {}  # {model: {input_tokens, output_tokens}}
            self.initialized = True

    def get_client(self) -> AsyncOpenAI:
        """OpenAI 클라이언트 반환"""
        return self.client

    def get_model_config(self, model_id: str) -> ModelConfig:
        """모델 설정 조회"""
        if model_id not in MODEL_CATALOG:
            raise ValueError(f"Unknown model: {model_id}")
        return MODEL_CATALOG[model_id]

    def get_available_models(
        self,
        service_name: str,
        user_preference: Optional[ModelTier] = None,
    ) -> List[ModelConfig]:
        """서비스에서 사용 가능한 모델 목록 반환"""
        if service_name not in SERVICE_MODEL_POLICIES:
            raise ValueError(f"Unknown service: {service_name}")

        policy = SERVICE_MODEL_POLICIES[service_name]

        # 허용된 등급 필터링
        available = [
            model
            for model in MODEL_CATALOG.values()
            if model.tier in policy.allowed_tiers
        ]

        # 필수 기능 체크
        available = [
            model
            for model in available
            if all(cap in model.capabilities for cap in policy.required_capabilities)
        ]

        # 사용자 선호도 필터링 (선택)
        if user_preference:
            available = [m for m in available if m.tier == user_preference]

        # 가격순 정렬 (저렴한 것부터)
        available.sort(key=lambda m: m.input_price_per_1m)

        return available

    def get_default_model(self, service_name: str) -> str:
        """서비스 기본 모델 반환"""
        if service_name not in SERVICE_MODEL_POLICIES:
            raise ValueError(f"Unknown service: {service_name}")
        return SERVICE_MODEL_POLICIES[service_name].default_model

    def validate_model_for_service(
        self,
        service_name: str,
        model_id: str,
    ) -> bool:
        """서비스에서 모델 사용 가능 여부 검증"""
        if service_name not in SERVICE_MODEL_POLICIES:
            return False

        policy = SERVICE_MODEL_POLICIES[service_name]

        if model_id not in MODEL_CATALOG:
            return False

        model = MODEL_CATALOG[model_id]

        # 등급 체크
        if model.tier not in policy.allowed_tiers:
            return False

        # 필수 기능 체크
        if not all(cap in model.capabilities for cap in policy.required_capabilities):
            return False

        return True

    def track_usage(
        self,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ):
        """토큰 사용량 추적"""
        if model_id not in self.usage_tracker:
            self.usage_tracker[model_id] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_cost_usd": 0.0,
            }

        self.usage_tracker[model_id]["input_tokens"] += input_tokens
        self.usage_tracker[model_id]["output_tokens"] += output_tokens

        # 비용 계산
        model_config = self.get_model_config(model_id)
        input_cost = (input_tokens / 1_000_000) * model_config.input_price_per_1m
        output_cost = (output_tokens / 1_000_000) * model_config.output_price_per_1m

        self.usage_tracker[model_id]["total_cost_usd"] += input_cost + output_cost

    def get_usage_report(self) -> Dict[str, Any]:
        """사용량 리포트 반환"""
        return self.usage_tracker.copy()
```

---

### 2. RAG Integration (사용자 데이터 컨텍스트)

**위치**: `backend/app/services/gen_ai/core/rag_service.py`

```python
"""
RAG Service

목적:
- 사용자 데이터 벡터화 (Backtest 결과, 전략 성과 등)
- 유사도 검색 (벡터 DB: ChromaDB 또는 Pinecone)
- LLM 프롬프트에 컨텍스트 주입
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import chromadb
from chromadb.config import Settings


class RAGContext(BaseModel):
    """RAG 컨텍스트 (검색 결과)"""
    document_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float


class RAGService:
    """RAG 서비스 (Retrieval-Augmented Generation)"""

    def __init__(self):
        """ChromaDB 클라이언트 초기화"""
        # 로컬 ChromaDB (개발)
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./data/chromadb"
        ))

        # 컬렉션 생성/조회
        self.backtests_collection = self.client.get_or_create_collection(
            name="user_backtests",
            metadata={"description": "사용자 백테스트 결과"}
        )

        self.strategies_collection = self.client.get_or_create_collection(
            name="user_strategies",
            metadata={"description": "사용자 전략 코드 및 성과"}
        )

    async def index_backtest_result(
        self,
        backtest_id: str,
        user_id: str,
        result_summary: Dict[str, Any],
    ):
        """백테스트 결과를 벡터 DB에 인덱싱"""

        # 백테스트 결과를 텍스트로 변환
        text_content = self._format_backtest_as_text(result_summary)

        # 메타데이터
        metadata = {
            "backtest_id": backtest_id,
            "user_id": user_id,
            "strategy_name": result_summary.get("strategy_name", "Unknown"),
            "total_return": result_summary.get("total_return", 0.0),
            "sharpe_ratio": result_summary.get("sharpe_ratio", 0.0),
            "created_at": datetime.now().isoformat(),
        }

        # ChromaDB에 추가
        self.backtests_collection.add(
            documents=[text_content],
            metadatas=[metadata],
            ids=[backtest_id],
        )

    async def search_similar_backtests(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> List[RAGContext]:
        """사용자의 유사 백테스트 검색"""

        # ChromaDB 쿼리
        results = self.backtests_collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"user_id": user_id},  # 사용자 필터링
        )

        # RAGContext로 변환
        contexts: List[RAGContext] = []
        for i in range(len(results["ids"][0])):
            contexts.append(
                RAGContext(
                    document_id=results["ids"][0][i],
                    content=results["documents"][0][i],
                    metadata=results["metadatas"][0][i],
                    similarity_score=results["distances"][0][i],
                )
            )

        return contexts

    async def build_rag_prompt(
        self,
        user_query: str,
        user_id: str,
        context_type: str = "backtests",
        top_k: int = 3,
    ) -> str:
        """RAG 프롬프트 생성 (사용자 데이터 컨텍스트 포함)"""

        # 유사 문서 검색
        if context_type == "backtests":
            contexts = await self.search_similar_backtests(user_id, user_query, top_k)
        else:
            contexts = []  # 다른 타입 추가 가능

        # 프롬프트 구성
        if not contexts:
            return user_query

        context_text = "\n\n".join([
            f"[참고 {i+1}] {ctx.content}"
            for i, ctx in enumerate(contexts)
        ])

        prompt = f"""다음은 사용자의 과거 백테스트 결과입니다:

{context_text}

사용자 요청: {user_query}

위 과거 데이터를 참고하여 답변해주세요."""

        return prompt

    def _format_backtest_as_text(self, result: Dict[str, Any]) -> str:
        """백테스트 결과를 텍스트로 포맷팅"""
        return f"""
전략명: {result.get('strategy_name', 'Unknown')}
기간: {result.get('start_date', 'N/A')} ~ {result.get('end_date', 'N/A')}
총 수익률: {result.get('total_return', 0.0):.2%}
샤프 비율: {result.get('sharpe_ratio', 0.0):.2f}
최대 낙폭: {result.get('max_drawdown', 0.0):.2%}
총 거래 횟수: {result.get('total_trades', 0)}
승률: {result.get('win_rate', 0.0):.2%}
"""
```

---

### 3. 서비스별 적용 예시

**3.1 StrategyBuilderService (RAG + 모델 선택)**

```python
# backend/app/services/gen_ai/applications/strategy_builder_service.py

from app.services.gen_ai.core.openai_client_manager import OpenAIClientManager
from app.services.gen_ai.core.rag_service import RAGService

class StrategyBuilderService:
    def __init__(
        self,
        strategy_service,
        backtest_service,
    ):
        self.strategy_service = strategy_service
        self.backtest_service = backtest_service

        # 중앙화된 OpenAI 클라이언트 사용
        self.openai_manager = OpenAIClientManager()
        self.client = self.openai_manager.get_client()

        # RAG 서비스
        self.rag_service = RAGService()

        # 기본 모델 (사용자 선택 가능)
        self.default_model = self.openai_manager.get_default_model("strategy_builder")

    async def generate_strategy_with_rag(
        self,
        user_id: str,
        user_request: str,
        model_preference: Optional[str] = None,  # 사용자 모델 선택
    ) -> str:
        """RAG 기반 전략 생성 (사용자 과거 백테스트 참고)"""

        # 모델 선택 및 검증
        model_id = model_preference or self.default_model

        if not self.openai_manager.validate_model_for_service("strategy_builder", model_id):
            raise ValueError(f"Model {model_id} not allowed for strategy_builder")

        # RAG 프롬프트 생성 (사용자 과거 백테스트 검색)
        rag_prompt = await self.rag_service.build_rag_prompt(
            user_query=user_request,
            user_id=user_id,
            context_type="backtests",
            top_k=3,
        )

        # LLM 호출
        response = await self.client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": "당신은 퀀트 트레이딩 전략 전문가입니다. 사용자의 과거 백테스트 결과를 참고하여 최적의 전략 코드를 생성하세요.",
                },
                {
                    "role": "user",
                    "content": rag_prompt,
                },
            ],
        )

        # 토큰 사용량 추적
        usage = response.usage
        self.openai_manager.track_usage(
            model_id=model_id,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
        )

        return response.choices[0].message.content
```

**3.2 API 엔드포인트 (모델 선택)**

```python
# backend/app/api/routes/gen_ai/strategy_builder.py

from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.services.gen_ai.core.openai_client_manager import (
    OpenAIClientManager,
    ModelTier,
    ModelConfig,
)
from app.services.gen_ai.applications.strategy_builder_service import (
    StrategyBuilderService,
)

router = APIRouter()


class ModelSelectionRequest(BaseModel):
    """모델 선택 요청"""
    preferred_tier: Optional[ModelTier] = None  # 사용자 선호 등급


class StrategyGenerateRequest(BaseModel):
    """전략 생성 요청"""
    user_request: str
    model_id: Optional[str] = None  # 사용자 모델 선택 (선택)


@router.get("/models")
async def get_available_models(
    tier: Optional[ModelTier] = None,
) -> List[ModelConfig]:
    """전략 빌더에서 사용 가능한 모델 목록 조회"""
    manager = OpenAIClientManager()
    models = manager.get_available_models(
        service_name="strategy_builder",
        user_preference=tier,
    )
    return models


@router.post("/generate")
async def generate_strategy_with_model(
    request: StrategyGenerateRequest,
    service: StrategyBuilderService = Depends(),
    user_id: str = Depends(get_current_user_id),
) -> Dict[str, Any]:
    """RAG 기반 전략 생성 (모델 선택 가능)"""

    strategy_code = await service.generate_strategy_with_rag(
        user_id=user_id,
        user_request=request.user_request,
        model_preference=request.model_id,
    )

    return {
        "strategy_code": strategy_code,
        "model_used": request.model_id or service.default_model,
    }
```

---

## 📊 적용 범위 및 우선순위

### Phase 1: 기본 인프라 (1주)

1. ✅ **OpenAIClientManager 구현** (2일)
   - 모델 카탈로그
   - 서비스별 정책
   - 토큰 추적
2. ✅ **서비스 리팩토링** (3일)
   - StrategyBuilderService
   - NarrativeReportService
   - ChatOpsAdvancedService
   - PromptGovernanceService
3. ✅ **API 엔드포인트** (2일)
   - 모델 선택 API
   - 사용량 조회 API

### Phase 2: RAG 통합 (1주)

1. ✅ **RAGService 구현** (2일)
   - ChromaDB 설정
   - 백테스트 인덱싱
   - 유사도 검색
2. ✅ **서비스 통합** (3일)
   - StrategyBuilderService RAG 적용
   - ChatOpsAdvancedService RAG 적용
   - 백테스트 완료 시 자동 인덱싱
3. ✅ **테스트 및 검증** (2일)
   - RAG 품질 테스트
   - 성능 벤치마크

### Phase 3: 고급 기능 (선택적)

1. ⏸️ **Function Calling 통합**
   - 실시간 데이터 조회
   - 백테스트 자동 실행
2. ⏸️ **비용 최적화**
   - 캐싱 레이어
   - 프롬프트 압축
3. ⏸️ **모니터링 대시보드**
   - 모델별 사용량
   - 비용 추적
   - 성능 지표

---

## 💰 비용 최적화 전략

### 1. 모델별 사용 사례

| 서비스           | 작업 유형            | 권장 모델   | 월간 예상 비용\* |
| ---------------- | -------------------- | ----------- | ---------------- |
| NarrativeReport  | 백테스트 리포트 생성 | gpt-4o-mini | $5-10            |
| StrategyBuilder  | 전략 코드 생성       | gpt-4o      | $20-50           |
| ChatOpsAdvanced  | 일반 대화            | gpt-4o-mini | $2-5             |
| PromptGovernance | 정책 체크            | gpt-4o-mini | $1-2             |

\*_1000명 사용자 기준, 월 10,000 요청 가정_

### 2. 비용 절감 팁

1. **작업별 모델 분리**: 단순 요약 → mini, 복잡한 코드 → advanced
2. **캐싱**: 동일 요청 → 재사용 (50% 비용 절감)
3. **프롬프트 최적화**: 불필요한 예시 제거 → 토큰 30% 절감
4. **RAG 활용**: 전체 데이터 주입 대신 관련 데이터만 → 70% 토큰 절감

---

## 🔐 보안 및 거버넌스

### 1. API 키 관리

- ✅ 환경변수 (.env)
- ✅ 서비스별 rate limiting
- ✅ 사용자별 quota

### 2. 프롬프트 거버넌스

- ✅ PromptGovernanceService 활용
- ✅ 금지어 필터링
- ✅ PII 데이터 마스킹

### 3. 모니터링

- ✅ 토큰 사용량 추적
- ✅ 비용 알림 (임계값 초과 시)
- ✅ 모델별 성능 메트릭

---

## 📝 마이그레이션 체크리스트

### 기존 코드 제거

- [ ] ❌ `narrative_report_service.py` - `self.client = AsyncOpenAI()` 삭제
- [ ] ❌ `strategy_builder_service.py` - `self.client = AsyncOpenAI()` 삭제
- [ ] ❌ `chatops_advanced_service.py` - `self.client = AsyncOpenAI()` 삭제

### 새 코드 추가

- [ ] ✅ `gen_ai/core/openai_client_manager.py` 생성
- [ ] ✅ `gen_ai/core/rag_service.py` 생성
- [ ] ✅ 각 서비스에 `OpenAIClientManager` 주입
- [ ] ✅ API 라우터에 모델 선택 엔드포인트 추가

### 환경 변수

- [ ] ✅ `OPENAI_API_KEY` 확인
- [ ] ✅ `CHROMADB_PATH` 추가 (선택)

### 테스트

- [ ] ✅ 모델 카탈로그 단위 테스트
- [ ] ✅ RAG 검색 통합 테스트
- [ ] ✅ 서비스별 E2E 테스트

---

## 🎯 추가 아이디어

### 1. 멀티모달 지원 (Vision API)

- 차트 이미지 분석 (백테스트 결과 차트)
- 기술적 분석 패턴 인식

### 2. Fine-tuning (선택적)

- 사용자 전략 스타일 학습
- 도메인 특화 모델 (퀀트 트레이딩)

### 3. Streaming 응답

- 긴 리포트 생성 시 실시간 스트리밍
- 사용자 경험 개선

### 4. A/B Testing

- 모델별 성능 비교 (품질 vs 비용)
- 최적 모델 자동 선택

---

## 📚 참고 자료

- [OpenAI Pricing (2025)](https://openai.com/pricing)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Best Practices](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

---

**다음 단계**: Phase 1 구현 시작 (OpenAIClientManager)
