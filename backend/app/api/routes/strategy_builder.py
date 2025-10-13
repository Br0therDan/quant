"""
Strategy Builder API Routes

Phase 3 D2: Interactive Strategy Builder
자연어 기반 대화형 전략 빌더 엔드포인트
"""

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.strategy_builder import (
    IndicatorSearchRequest,
    IndicatorSearchResponse,
    StrategyApprovalRequest,
    StrategyApprovalResponse,
    StrategyBuilderRequest,
    StrategyBuilderResponse,
)
from app.services.service_factory import service_factory

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=StrategyBuilderResponse)
async def generate_strategy(
    request: StrategyBuilderRequest,
):
    """
    자연어 입력으로 트레이딩 전략 생성

    **워크플로우:**
    1. 자연어 쿼리 → LLM 의도 파싱 (IntentType 분류)
    2. 엔티티 추출 (지표, 파라미터, 심볼 등)
    3. 지표 추천 (임베딩 기반 유사도 매칭)
    4. 파라미터 검증 (범위, 타입 체크)
    5. 전략 설정 생성 (GeneratedStrategyConfig)
    6. 휴먼 승인 필요성 평가

    **예시 요청:**
    - "RSI가 30 이하일 때 매수하고, 70 이상일 때 매도하는 전략을 만들어줘"
    - "MACD와 Bollinger Bands를 사용한 추세 추종 전략 추천해줘"
    - "단기 매매에 적합한 EMA 크로스오버 전략을 테스트하고 싶어"

    **응답:**
    - `status`: "success" | "warning" | "error"
    - `parsed_intent`: LLM이 파싱한 사용자 의도 (IntentType, 신뢰도, 추출된 엔티티)
    - `generated_strategy`: 생성된 전략 설정 (지표, 파라미터, 진입/청산 조건)
    - `human_approval`: 승인 필요 여부 + 이유 + 수정 제안
    - `overall_confidence`: 전체 신뢰도 (0.0-1.0)

    **주의사항:**
    - OpenAI API 키 필요 (`OPENAI_API_KEY` 환경변수)
    - 자연어 쿼리는 10-1000자 제한
    - 생성된 전략은 기본적으로 승인 필요 (`require_human_approval=True`)
    - 낮은 신뢰도 (<0.5) 시 대안 제안 제공
    """
    try:
        strategy_builder_service = service_factory.get_strategy_builder_service()
        response = await strategy_builder_service.build_strategy(request)

        logger.info(
            "Strategy generation completed",
            extra={
                "query": request.query[:100],
                "intent": response.parsed_intent.intent_type.value,
                "confidence": response.overall_confidence,
                "processing_time_ms": response.processing_time_ms,
            },
        )

        return response

    except ValueError as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"입력 검증 실패: {str(e)}",
        )

    except Exception as e:
        logger.error(f"Strategy generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"전략 생성 실패: {str(e)}",
        ) from e


@router.post("/approve", response_model=StrategyApprovalResponse)
async def approve_strategy(
    approval_request: StrategyApprovalRequest,
):
    """
    생성된 전략 승인 처리 (Human-in-the-Loop)

    **워크플로우:**
    1. 생성된 전략 ID 조회 (`strategy_builder_response_id`)
    2. 승인 여부 확인 (`approved`: true/false)
    3. 수정 사항 적용 (`modifications`: Dict)
    4. 실제 전략 생성 (StrategyService)
    5. 승인 로그 기록 (audit trail)

    **승인 시나리오:**
    - **승인 (approved=true)**: 수정 없이 전략 생성
    - **수정 후 승인 (approved=true + modifications)**: 파라미터 수정 후 생성
    - **거부 (approved=false)**: 전략 생성 취소, 사유 기록

    **응답:**
    - `status`: "approved" | "modified" | "rejected"
    - `message`: 승인 결과 메시지
    - `strategy_id`: 생성된 전략 ID (승인 시)
    - `approved_at`: 승인 시각 (ISO 8601)

    **예시:**
    ```json
    {
        "strategy_builder_response_id": "abc123",
        "approved": true,
        "modifications": {
            "rsi_period": 21,
            "rsi_oversold": 25
        },
        "approval_notes": "RSI 기간을 21로 조정하여 시장 변동성 반영"
    }
    ```
    """
    try:
        # TODO: 실제 승인 로직 구현
        # 1. strategy_builder_response_id로 원본 전략 조회
        # 2. modifications 적용
        # 3. StrategyService로 실제 전략 생성
        # 4. 승인 로그 저장 (MongoDB)

        # 임시 응답 (실제 구현 필요)
        if approval_request.approved:
            status = "modified" if approval_request.modifications else "approved"
            message = (
                "전략이 승인되어 생성되었습니다."
                if not approval_request.modifications
                else "수정 사항이 적용되어 전략이 생성되었습니다."
            )
            strategy_id = (
                "temp_strategy_id_" + approval_request.strategy_builder_response_id
            )

            logger.info(
                "Strategy approved",
                extra={
                    "strategy_builder_response_id": approval_request.strategy_builder_response_id,
                    "status": status,
                    "has_modifications": bool(approval_request.modifications),
                },
            )

            return StrategyApprovalResponse(
                status=status,
                message=message,
                strategy_id=strategy_id,
            )
        else:
            logger.info(
                "Strategy rejected",
                extra={
                    "strategy_builder_response_id": approval_request.strategy_builder_response_id,
                    "approval_notes": approval_request.approval_notes,
                },
            )

            return StrategyApprovalResponse(
                status="rejected",
                message="전략이 거부되었습니다.",
                strategy_id=None,
            )

    except Exception as e:
        logger.error(f"Strategy approval failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"전략 승인 처리 실패: {str(e)}",
        ) from e


@router.post("/search-indicators", response_model=IndicatorSearchResponse)
async def search_indicators(
    search_request: IndicatorSearchRequest,
):
    """
    임베딩 기반 지표 검색

    **기능:**
    - 자연어 쿼리 → 임베딩 변환
    - 지표 지식 베이스와 코사인 유사도 계산
    - 상위 K개 지표 추천 (기본 5개)

    **사용 사례:**
    - "변동성을 측정하는 지표를 찾아줘" → Bollinger Bands, ATR
    - "추세 전환을 포착하는 지표" → MACD, EMA Crossover
    - "모멘텀 지표" → RSI, Stochastic, CCI

    **응답:**
    - `status`: "success" | "error"
    - `indicators`: 추천 지표 목록 (유사도 순)
    - `total`: 반환된 지표 수
    - `query_embedding`: (디버깅용) 쿼리 임베딩 벡터

    **예시:**
    ```json
    {
        "query": "변동성 측정 지표",
        "top_k": 3,
        "filters": {"type": "volatility"}
    }
    ```
    """
    try:
        # TODO: 실제 임베딩 검색 로직 구현
        # 1. query → OpenAI text-embedding-ada-002
        # 2. 지표 지식 베이스와 코사인 유사도 계산
        # 3. top_k 필터링
        # 4. filters 적용 (type, category 등)

        # 임시 응답 (실제 구현 필요)
        from app.schemas.strategy_builder import IndicatorRecommendation

        indicators = [
            IndicatorRecommendation(
                indicator_name="RSI",
                indicator_type="momentum",
                confidence=0.9,
                rationale="과매수/과매도를 판단하는 대표적인 모멘텀 지표",
                suggested_parameters={"period": 14, "overbought": 70, "oversold": 30},
                similarity_score=0.85,
            ),
            IndicatorRecommendation(
                indicator_name="MACD",
                indicator_type="trend",
                confidence=0.85,
                rationale="추세 전환을 포착하는 이동평균 다이버전스 지표",
                suggested_parameters={
                    "fast_period": 12,
                    "slow_period": 26,
                    "signal_period": 9,
                },
                similarity_score=0.78,
            ),
        ]

        logger.info(
            "Indicator search completed",
            extra={
                "query": search_request.query,
                "top_k": search_request.top_k,
                "results": len(indicators),
            },
        )

        return IndicatorSearchResponse(
            status="success",
            indicators=indicators[: search_request.top_k],
            total=len(indicators),
            query_embedding=None,  # 디버깅 시 활성화
        )

    except Exception as e:
        logger.error(f"Indicator search failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"지표 검색 실패: {str(e)}",
        ) from e
