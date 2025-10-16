"""
Strategy 데이터 마이그레이션 스크립트
기존 strategies 컬렉션의 문서들을 새로운 스키마로 마이그레이션
"""

import logging
from typing import Any

from app.models.trading.strategy import Strategy, StrategyType
from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)

logger = logging.getLogger(__name__)


async def migrate_strategy_documents() -> None:
    """
    기존 Strategy 문서를 새로운 스키마로 마이그레이션
    - parameters 필드 → config 필드로 변환
    """
    logger.info("Starting Strategy document migration...")

    try:
        # 모든 기존 전략 조회 (config가 없는 것들)
        strategies = await Strategy.find(Strategy.config is None).to_list()

        if not strategies:
            logger.info("No strategies to migrate")
            return

        logger.info(f"Found {len(strategies)} strategies to migrate")

        migrated_count = 0
        error_count = 0

        for strategy in strategies:
            try:
                # 기존 parameters 필드가 있는지 확인
                raw_doc = await Strategy.get_motor_collection().find_one(
                    {"_id": strategy.id}
                )

                if not raw_doc:
                    logger.warning(
                        f"Strategy {strategy.id} not found in raw collection"
                    )
                    continue

                parameters = raw_doc.get("parameters", {})

                # parameters가 없으면 기본값으로 config 생성
                if not parameters:
                    parameters = _get_default_parameters(strategy.strategy_type)

                # config 생성
                config = _build_config(strategy.strategy_type, parameters)

                # Strategy 업데이트
                strategy.config = config
                await strategy.save()

                migrated_count += 1
                logger.info(
                    f"✅ Migrated strategy: {strategy.name} ({strategy.strategy_type})"
                )

            except Exception as e:
                error_count += 1
                logger.error(f"❌ Failed to migrate strategy {strategy.name}: {e}")

        logger.info(
            f"Migration completed: {migrated_count} success, {error_count} errors"
        )

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)


def _build_config(strategy_type: StrategyType, parameters: dict[str, Any]):
    """parameters dict를 타입별 Config 객체로 변환"""
    common_defaults = {
        "lookback_period": 252,
        "min_data_points": 30,
        "max_position_size": 1.0,
    }

    if strategy_type == StrategyType.SMA_CROSSOVER:
        return SMACrossoverConfig(
            config_type="sma_crossover",
            **common_defaults,
            **parameters,
        )
    elif strategy_type == StrategyType.RSI_MEAN_REVERSION:
        return RSIMeanReversionConfig(
            config_type="rsi_mean_reversion",
            **common_defaults,
            **parameters,
        )
    elif strategy_type == StrategyType.MOMENTUM:
        return MomentumConfig(
            config_type="momentum",
            **common_defaults,
            **parameters,
        )
    elif strategy_type == StrategyType.BUY_AND_HOLD:
        return BuyAndHoldConfig(
            config_type="buy_and_hold",
            **common_defaults,
            **parameters,
        )
    else:
        # 알 수 없는 타입은 Buy&Hold 기본값 사용
        logger.warning(
            f"Unknown strategy type: {strategy_type}, using Buy&Hold defaults"
        )
        return BuyAndHoldConfig(
            config_type="buy_and_hold",
            **common_defaults,
        )


def _get_default_parameters(strategy_type: StrategyType) -> dict[str, Any]:
    """전략 타입별 기본 parameters 반환"""
    defaults = {
        StrategyType.SMA_CROSSOVER: {
            "short_window": 10,
            "long_window": 30,
            "min_crossover_strength": 0.01,
        },
        StrategyType.RSI_MEAN_REVERSION: {
            "rsi_period": 14,
            "oversold_threshold": 30.0,
            "overbought_threshold": 70.0,
            "confirmation_periods": 2,
        },
        StrategyType.MOMENTUM: {
            "momentum_period": 20,
            "buy_threshold": 0.02,
            "sell_threshold": -0.02,
            "volume_filter": True,
            "min_volume_ratio": 1.5,
            "top_n_stocks": 5,
            "rebalance_frequency": "monthly",
        },
        StrategyType.BUY_AND_HOLD: {},
    }

    return defaults.get(strategy_type, {})
