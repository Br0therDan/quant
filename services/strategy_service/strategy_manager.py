"""전략 관리 시스템

모든 거래 전략을 통합 관리하는 시스템
- 전략 등록 및 검색
- Pydantic 기반 설정 검증
- JSON 템플릿 시스템
- 전략 직렬화/역직렬화
- 전략 성과 비교 및 분석
"""

import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
from pydantic import BaseModel, Field, ValidationError

from .base_strategy import BaseStrategy, SignalType, StrategyConfig
from .buy_and_hold import (
    BuyAndHoldConfig,
    BuyAndHoldStrategy,
    create_buy_and_hold_strategy,
)
from .momentum import MomentumConfig, MomentumStrategy, create_momentum_strategy
from .rsi_mean_reversion import RSIConfig, RSIMeanReversionStrategy, create_rsi_strategy
from .sma_crossover import (
    SMAConfig,
    SMACrossoverStrategy,
    create_sma_crossover_strategy,
)


class StrategyType(str, Enum):
    """지원되는 전략 타입"""

    SMA_CROSSOVER = "sma_crossover"
    RSI_MEAN_REVERSION = "rsi_mean_reversion"
    MOMENTUM = "momentum"
    BUY_AND_HOLD = "buy_and_hold"


class StrategyTemplate(BaseModel):
    """전략 템플릿"""

    name: str = Field(..., description="전략 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: str = Field(..., description="전략 설명")
    parameters: dict[str, Any] = Field(default_factory=dict, description="전략 파라미터")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")
    tags: list[str] = Field(default_factory=list, description="태그")

    class Config:
        use_enum_values = True


class StrategyPerformance(BaseModel):
    """전략 성과 정보"""

    strategy_name: str
    total_signals: int
    buy_signals: int
    sell_signals: int
    total_return: Optional[float] = None
    win_rate: Optional[float] = None
    avg_return_per_trade: Optional[float] = None
    max_drawdown: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class StrategyManager:
    """전략 관리자"""

    # 전략 타입별 클래스 매핑
    STRATEGY_CLASSES: dict[StrategyType, type[BaseStrategy]] = {
        StrategyType.SMA_CROSSOVER: SMACrossoverStrategy,
        StrategyType.RSI_MEAN_REVERSION: RSIMeanReversionStrategy,
        StrategyType.MOMENTUM: MomentumStrategy,
        StrategyType.BUY_AND_HOLD: BuyAndHoldStrategy,
    }

    # 설정 클래스 매핑
    CONFIG_CLASSES: dict[StrategyType, type[StrategyConfig]] = {
        StrategyType.SMA_CROSSOVER: SMAConfig,
        StrategyType.RSI_MEAN_REVERSION: RSIConfig,
        StrategyType.MOMENTUM: MomentumConfig,
        StrategyType.BUY_AND_HOLD: BuyAndHoldConfig,
    }

    # 생성 함수 매핑
    FACTORY_FUNCTIONS = {
        StrategyType.SMA_CROSSOVER: create_sma_crossover_strategy,
        StrategyType.RSI_MEAN_REVERSION: create_rsi_strategy,
        StrategyType.MOMENTUM: create_momentum_strategy,
        StrategyType.BUY_AND_HOLD: create_buy_and_hold_strategy,
    }

    def __init__(self, templates_dir: str = "strategy_templates"):
        """
        Args:
            templates_dir: 전략 템플릿 저장 디렉토리
        """
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        # 등록된 전략들
        self._strategies: dict[str, BaseStrategy] = {}
        self._templates: dict[str, StrategyTemplate] = {}

        # 기본 템플릿 생성
        self._create_default_templates()
        self._load_templates()

    def _create_default_templates(self) -> None:
        """기본 전략 템플릿 생성"""
        default_templates = [
            {
                "name": "Conservative SMA Crossover",
                "strategy_type": StrategyType.SMA_CROSSOVER,
                "description": "보수적인 SMA 교차 전략 (장기 추세 추종)",
                "parameters": {
                    "short_window": 20,
                    "long_window": 50,
                    "min_signal_strength": 0.6,
                },
                "tags": ["conservative", "trend_following", "long_term"],
            },
            {
                "name": "Standard RSI Mean Reversion",
                "strategy_type": StrategyType.RSI_MEAN_REVERSION,
                "description": "표준 RSI 평균회귀 전략",
                "parameters": {
                    "rsi_period": 14,
                    "oversold_threshold": 30,
                    "overbought_threshold": 70,
                    "use_sma_filter": True,
                },
                "tags": ["mean_reversion", "rsi", "standard"],
            },
            {
                "name": "Balanced Momentum",
                "strategy_type": StrategyType.MOMENTUM,
                "description": "균형잡힌 모멘텀 전략",
                "parameters": {
                    "momentum_period": 10,
                    "price_change_threshold": 0.02,
                    "volume_multiplier": 1.5,
                    "use_trend_filter": True,
                    "use_dynamic_threshold": True,
                },
                "tags": ["momentum", "balanced", "trend_following"],
            },
            {
                "name": "Standard Buy and Hold",
                "strategy_type": StrategyType.BUY_AND_HOLD,
                "description": "표준 매수 후 보유 전략",
                "parameters": {
                    "hold_period_days": None,
                    "auto_sell_at_end": True,
                    "enable_dca": False,
                },
                "tags": ["buy_and_hold", "benchmark", "passive"],
            },
        ]

        for template_data in default_templates:
            template = StrategyTemplate(**template_data)
            self._save_template(template)

    def _save_template(self, template: StrategyTemplate) -> None:
        """템플릿을 파일로 저장"""
        filename = f"{template.name.lower().replace(' ', '_')}.json"
        filepath = self.templates_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                template.model_dump(), f, indent=2, ensure_ascii=False, default=str
            )

    def _load_templates(self) -> None:
        """저장된 템플릿들 로드"""
        self._templates.clear()

        for filepath in self.templates_dir.glob("*.json"):
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                template = StrategyTemplate(**data)
                self._templates[template.name] = template

            except (json.JSONDecodeError, ValidationError) as e:
                print(f"템플릿 로드 실패 {filepath}: {e}")

    def get_available_strategy_types(self) -> list[str]:
        """사용 가능한 전략 타입 반환"""
        return [strategy_type.value for strategy_type in StrategyType]

    def create_strategy(
        self,
        strategy_type: Union[str, StrategyType],
        name: Optional[str] = None,
        **parameters: Any,
    ) -> BaseStrategy:
        """전략 생성"""
        if isinstance(strategy_type, str):
            strategy_type = StrategyType(strategy_type)

        if strategy_type not in self.FACTORY_FUNCTIONS:
            raise ValueError(f"지원되지 않는 전략 타입: {strategy_type}")

        # 기본 이름 설정
        if name is None:
            name = f"{strategy_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 팩토리 함수로 전략 생성
        factory_func = self.FACTORY_FUNCTIONS[strategy_type]
        strategy = factory_func(name=name, **parameters)

        # 전략 등록
        self._strategies[name] = strategy

        return strategy

    def create_strategy_from_template(
        self,
        template_name: str,
        strategy_name: Optional[str] = None,
        **override_parameters: Any,
    ) -> BaseStrategy:
        """템플릿으로부터 전략 생성"""
        if template_name not in self._templates:
            raise ValueError(f"템플릿을 찾을 수 없음: {template_name}")

        template = self._templates[template_name]

        # 템플릿 파라미터에 오버라이드 적용
        parameters = template.parameters.copy()
        parameters.update(override_parameters)

        # 전략 이름 설정
        if strategy_name is None:
            strategy_name = (
                f"{template.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        return self.create_strategy(
            strategy_type=template.strategy_type, name=strategy_name, **parameters
        )

    def list_templates(
        self, strategy_type: Optional[Union[str, StrategyType]] = None
    ) -> list[StrategyTemplate]:
        """템플릿 목록 반환"""
        templates = list(self._templates.values())

        if strategy_type:
            if isinstance(strategy_type, str):
                strategy_type = StrategyType(strategy_type)
            templates = [t for t in templates if t.strategy_type == strategy_type]

        return sorted(templates, key=lambda x: x.name)

    def analyze_strategy_performance(
        self, strategy: BaseStrategy, data: pd.DataFrame
    ) -> StrategyPerformance:
        """전략 성과 분석"""
        signals = strategy.run(data)

        # 기본 통계
        total_signals = len(signals)
        buy_signals = sum(1 for s in signals if s.signal_type == SignalType.BUY)
        sell_signals = sum(1 for s in signals if s.signal_type == SignalType.SELL)

        # 수익률 계산
        total_return = None
        win_rate = None
        avg_return_per_trade = None

        if buy_signals > 0 and sell_signals > 0:
            # 매수-매도 쌍으로 거래 분석
            trades = []
            buy_signals_list = [s for s in signals if s.signal_type == SignalType.BUY]
            sell_signals_list = [s for s in signals if s.signal_type == SignalType.SELL]

            for i in range(min(len(buy_signals_list), len(sell_signals_list))):
                buy_price = buy_signals_list[i].price
                sell_price = sell_signals_list[i].price
                trade_return = (sell_price - buy_price) / buy_price
                trades.append(trade_return)

            if trades:
                total_return = sum(trades)
                avg_return_per_trade = total_return / len(trades)
                win_rate = sum(1 for t in trades if t > 0) / len(trades)

        # 날짜 범위
        start_date = signals[0].timestamp if signals else None
        end_date = signals[-1].timestamp if signals else None

        return StrategyPerformance(
            strategy_name=strategy.name,
            total_signals=total_signals,
            buy_signals=buy_signals,
            sell_signals=sell_signals,
            total_return=total_return,
            win_rate=win_rate,
            avg_return_per_trade=avg_return_per_trade,
            start_date=start_date,
            end_date=end_date,
        )

    def compare_strategies(
        self, strategies: list[BaseStrategy], data: pd.DataFrame
    ) -> pd.DataFrame:
        """여러 전략 성과 비교"""
        results = []

        for strategy in strategies:
            performance = self.analyze_strategy_performance(strategy, data)
            results.append(
                {
                    "strategy_name": performance.strategy_name,
                    "total_signals": performance.total_signals,
                    "buy_signals": performance.buy_signals,
                    "sell_signals": performance.sell_signals,
                    "total_return": performance.total_return,
                    "avg_return_per_trade": performance.avg_return_per_trade,
                    "win_rate": performance.win_rate,
                }
            )

        return pd.DataFrame(results)

    def validate_strategy_config(self, strategy_type: str, config: dict) -> bool:
        """전략 설정 검증"""
        try:
            if strategy_type not in [st.value for st in StrategyType]:
                return False

            # StrategyType으로 변환
            strategy_enum = StrategyType(strategy_type)

            # CONFIG_CLASSES에서 해당 설정 클래스 가져와서 검증
            if strategy_enum in self.CONFIG_CLASSES:
                config_class = self.CONFIG_CLASSES[strategy_enum]
                config_class(**config)
                return True

            return False
        except Exception:
            return False


# 전역 전략 매니저 인스턴스
strategy_manager = StrategyManager()


def get_strategy_manager() -> StrategyManager:
    """전역 전략 매니저 반환"""
    return strategy_manager
