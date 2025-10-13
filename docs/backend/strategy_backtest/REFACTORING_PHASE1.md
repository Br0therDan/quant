# Strategy & Backtest 리팩토링 실행 가이드

> **Phase 1 구현 가이드**: 긴급 개선 사항 (1-2주)  
> **목표**: 아키텍처 안정화, 중복 제거, 타입 안전성 확보

## 📋 목차

1. [P1.1 의존성 주입 개선](#p11-의존성-주입-개선)
2. [P1.2 중복 거래 로직 통합](#p12-중복-거래-로직-통합)
3. [P1.3 전략 파라미터 타입 안전성](#p13-전략-파라미터-타입-안전성)
4. [테스트 전략](#테스트-전략)
5. [배포 체크리스트](#배포-체크리스트)

---

## P1.1 의존성 주입 개선

### 문제 상황

현재 `BacktestService`는 불완전한 초기화 패턴을 사용합니다:

```python
# ❌ 현재 방식 (잘못됨)
class BacktestService:
    def __init__(self, ...):
        self.market_data_service = None  # 초기화 시 None
        self.strategy_service = None
        self.integrated_executor = None

    def set_dependencies(self, market_data_service, strategy_service):
        # 나중에 주입
        self.market_data_service = market_data_service
        self.strategy_service = strategy_service
        self.integrated_executor = IntegratedBacktestExecutor(...)
```

**문제점**:

1. 서비스 생성 직후 사용 불가
2. 의존성 누락 시 런타임 에러
3. 테스트 어려움

### 개선 방안

#### Step 1: BacktestService 생성자 수정

```python
# ✅ 개선된 방식
# backend/app/services/backtest_service.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.services.market_data_service import MarketDataService
    from app.services.strategy_service import StrategyService
    from app.services.database_manager import DatabaseManager

class BacktestService:
    def __init__(
        self,
        market_data_service: "MarketDataService",
        strategy_service: "StrategyService",
        database_manager: "DatabaseManager",
    ):
        """백테스트 서비스 초기화

        Args:
            market_data_service: 시장 데이터 서비스
            strategy_service: 전략 서비스
            database_manager: 데이터베이스 매니저
        """
        # 의존성 검증
        if not market_data_service:
            raise ValueError("market_data_service is required")
        if not strategy_service:
            raise ValueError("strategy_service is required")
        if not database_manager:
            raise ValueError("database_manager is required")

        self.market_data_service = market_data_service
        self.strategy_service = strategy_service
        self.database_manager = database_manager

        # 통합 실행기 즉시 생성
        self.integrated_executor = IntegratedBacktestExecutor(
            market_data_service=market_data_service,
            strategy_service=strategy_service,
        )

        # 성과 계산기
        self.performance_calculator = PerformanceCalculator()

        logger.info("BacktestService initialized with all dependencies")
```

#### Step 2: ServiceFactory 업데이트

```python
# backend/app/services/service_factory.py

class ServiceFactory:
    # ... 기존 코드 ...

    def get_backtest_service(self) -> BacktestService:
        """백테스트 서비스 반환 (완전한 의존성 주입)"""
        if self._backtest_service is None:
            # 의존성 먼저 생성
            market_data_service = self.get_market_data_service()
            strategy_service = self.get_strategy_service()
            database_manager = self.get_database_manager()

            # 모든 의존성과 함께 생성
            self._backtest_service = BacktestService(
                market_data_service=market_data_service,
                strategy_service=strategy_service,
                database_manager=database_manager,
            )

            logger.info("BacktestService created with dependencies")

        return self._backtest_service
```

#### Step 3: set_dependencies 메서드 제거

```python
# backend/app/services/backtest_service.py

# ❌ 삭제할 코드
# def set_dependencies(self, market_data_service, strategy_service):
#     self.market_data_service = market_data_service
#     self.strategy_service = strategy_service
#     ...
```

#### Step 4: main.py 업데이트

```python
# backend/app/main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    try:
        # 1. 데이터베이스 초기화
        await init_db(app, document_models=collections)

        # 2. ServiceFactory 의존성 설정 (순서 중요!)
        database_manager = service_factory.get_database_manager()

        # 3. 서비스 생성 (자동으로 의존성 주입됨)
        _ = service_factory.get_market_data_service()
        _ = service_factory.get_strategy_service()
        _ = service_factory.get_backtest_service()  # 의존성 자동 연결

        # ❌ 제거: set_dependencies 호출 불필요
        # backtest_service.set_dependencies(...)

        logger.info("All services initialized successfully")

        yield
    finally:
        # 정리 작업
        pass
```

### 검증 방법

```python
# tests/test_service_factory.py

import pytest
from app.services.service_factory import service_factory

def test_backtest_service_dependencies():
    """백테스트 서비스 의존성 주입 검증"""
    # Given
    backtest_service = service_factory.get_backtest_service()

    # Then
    assert backtest_service.market_data_service is not None
    assert backtest_service.strategy_service is not None
    assert backtest_service.database_manager is not None
    assert backtest_service.integrated_executor is not None

def test_backtest_service_immediate_use():
    """백테스트 서비스 즉시 사용 가능 검증"""
    # Given
    backtest_service = service_factory.get_backtest_service()

    # When/Then (에러 없이 실행되어야 함)
    backtest = await backtest_service.create_backtest(
        name="Test",
        config=BacktestConfig(...),
    )
    assert backtest is not None
```

---

## P1.2 중복 거래 로직 통합

### 문제 상황

거래 실행 로직이 두 곳에 중복:

1. `BacktestService.TradingSimulator.simulate_trades()`
2. `IntegratedBacktestExecutor._execute_trades()`

**차이점**:

- 수수료 계산 방식 다름 (하드코딩 vs 설정)
- 슬리피지 처리 다름
- 포트폴리오 업데이트 로직 다름

### 개선 방안

#### Step 1: TradeEngine 클래스 생성

```python
# backend/app/services/backtest/trade_engine.py

from datetime import datetime
from typing import Optional
import uuid
import logging

from app.models.backtest import (
    BacktestConfig,
    Trade,
    TradeType,
    OrderType,
)

logger = logging.getLogger(__name__)


class Portfolio:
    """포트폴리오 상태 관리"""

    def __init__(self, initial_cash: float):
        self.cash = initial_cash
        self.positions: dict[str, float] = {}  # symbol -> quantity
        self.position_costs: dict[str, float] = {}  # symbol -> avg_cost

    @property
    def total_value(self) -> float:
        """총 포트폴리오 가치"""
        return self.cash + sum(
            qty * self.position_costs.get(symbol, 0)
            for symbol, qty in self.positions.items()
        )

    def update_position(
        self,
        symbol: str,
        quantity: float,
        price: float,
        is_buy: bool,
    ) -> None:
        """포지션 업데이트"""
        if is_buy:
            current_qty = self.positions.get(symbol, 0)
            current_cost = self.position_costs.get(symbol, 0)

            # 평균 단가 계산
            total_cost = (current_qty * current_cost) + (quantity * price)
            new_qty = current_qty + quantity
            new_avg_cost = total_cost / new_qty if new_qty > 0 else 0

            self.positions[symbol] = new_qty
            self.position_costs[symbol] = new_avg_cost
        else:
            self.positions[symbol] = self.positions.get(symbol, 0) - quantity
            if self.positions[symbol] <= 0:
                self.positions.pop(symbol, None)
                self.position_costs.pop(symbol, None)


class TradeCosts:
    """거래 비용 계산"""

    def __init__(self, commission_rate: float, slippage_rate: float):
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate

    def calculate(
        self,
        quantity: float,
        price: float,
        is_buy: bool = True,
    ) -> dict[str, float]:
        """거래 비용 계산

        Returns:
            {
                'gross_amount': 총액,
                'commission': 수수료,
                'slippage': 슬리피지,
                'total_cost': 총 비용 (매수) 또는 순수익 (매도)
            }
        """
        gross_amount = quantity * price
        commission = gross_amount * self.commission_rate
        slippage = gross_amount * self.slippage_rate

        if is_buy:
            total_cost = gross_amount + commission + slippage
        else:
            total_cost = gross_amount - commission - slippage

        return {
            'gross_amount': gross_amount,
            'commission': commission,
            'slippage': slippage,
            'total_cost': total_cost,
        }


class TradeEngine:
    """통합 거래 실행 엔진"""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trade_costs = TradeCosts(
            commission_rate=config.commission_rate,
            slippage_rate=config.slippage_rate,
        )

    def execute_order(
        self,
        symbol: str,
        quantity: float,
        price: float,
        order_type: OrderType,
        trade_type: TradeType,
        portfolio: Portfolio,
        timestamp: datetime,
        signal_id: Optional[str] = None,
    ) -> Optional[Trade]:
        """주문 실행

        Args:
            symbol: 심볼
            quantity: 수량
            price: 가격
            order_type: 주문 타입
            trade_type: 거래 타입 (매수/매도)
            portfolio: 포트폴리오
            timestamp: 거래 시간
            signal_id: 전략 신호 ID

        Returns:
            실행된 거래 또는 None (실행 불가 시)
        """
        is_buy = (trade_type == TradeType.BUY)

        # 1. 거래 비용 계산
        costs = self.trade_costs.calculate(quantity, price, is_buy)

        # 2. 거래 가능성 검증
        if is_buy:
            if portfolio.cash < costs['total_cost']:
                logger.warning(
                    f"Insufficient cash for BUY order: "
                    f"need {costs['total_cost']:.2f}, have {portfolio.cash:.2f}"
                )
                return None
        else:
            current_position = portfolio.positions.get(symbol, 0)
            if current_position < quantity:
                logger.warning(
                    f"Insufficient position for SELL order: "
                    f"need {quantity}, have {current_position}"
                )
                return None

        # 3. 거래 실행
        if is_buy:
            portfolio.cash -= costs['total_cost']
            portfolio.update_position(symbol, quantity, price, is_buy=True)
        else:
            portfolio.cash += costs['total_cost']
            portfolio.update_position(symbol, quantity, price, is_buy=False)

        # 4. 거래 기록 생성
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            symbol=symbol,
            trade_type=trade_type,
            order_type=order_type,
            quantity=quantity,
            price=price,
            timestamp=timestamp,
            commission=costs['commission'],
            slippage=costs['slippage'],
            strategy_signal_id=signal_id,
            notes=f"Portfolio value: {portfolio.total_value:.2f}",
        )

        logger.info(
            f"Trade executed: {trade_type} {quantity} {symbol} @ {price:.2f}"
        )

        return trade

    def execute_signal(
        self,
        signal: dict,
        portfolio: Portfolio,
        current_prices: dict[str, float],
        timestamp: datetime,
    ) -> Optional[Trade]:
        """전략 신호 기반 주문 실행

        Args:
            signal: 전략 신호 {'symbol': str, 'action': str, 'quantity': float}
            portfolio: 포트폴리오
            current_prices: 현재 가격 {symbol: price}
            timestamp: 거래 시간

        Returns:
            실행된 거래 또는 None
        """
        symbol = signal.get('symbol')
        action = signal.get('action')
        quantity = signal.get('quantity', 0)

        if not symbol or not action or quantity <= 0:
            return None

        price = current_prices.get(symbol)
        if not price or price <= 0:
            logger.warning(f"Invalid price for {symbol}: {price}")
            return None

        # 신호를 거래 타입으로 변환
        if action.upper() == 'BUY':
            trade_type = TradeType.BUY
        elif action.upper() == 'SELL':
            trade_type = TradeType.SELL
        else:
            logger.warning(f"Unknown action: {action}")
            return None

        return self.execute_order(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_type=OrderType.MARKET,
            trade_type=trade_type,
            portfolio=portfolio,
            timestamp=timestamp,
            signal_id=signal.get('signal_id'),
        )
```

#### Step 2: TradingSimulator 제거 및 TradeEngine 사용

```python
# backend/app/services/backtest_service.py

# ❌ 삭제할 코드
# class TradingSimulator:
#     def __init__(self, config: BacktestConfig):
#         ...
#     def simulate_trades(self, signals):
#         ...

# ✅ 새 코드
from app.services.backtest.trade_engine import TradeEngine, Portfolio

class BacktestService:
    # ... 기존 코드 ...

    async def execute_backtest(
        self,
        backtest_id: str,
        strategy_id: str,
    ) -> BacktestResult | None:
        """백테스트 실행"""
        # ...

        # TradeEngine 사용
        trade_engine = TradeEngine(config=backtest.config)
        portfolio = Portfolio(initial_cash=backtest.config.initial_cash)

        trades = []
        portfolio_values = [portfolio.total_value]

        for signal in signals:
            trade = trade_engine.execute_signal(
                signal=signal,
                portfolio=portfolio,
                current_prices=current_prices,
                timestamp=current_timestamp,
            )

            if trade:
                trades.append(trade)

            portfolio_values.append(portfolio.total_value)

        # ...
```

#### Step 3: IntegratedBacktestExecutor 업데이트

```python
# backend/app/services/integrated_backtest_executor.py

from app.services.backtest.trade_engine import TradeEngine, Portfolio

class IntegratedBacktestExecutor:
    # ... 기존 코드 ...

    async def _execute_simulation(
        self,
        strategy_instance,
        market_data: dict[str, list],
        initial_capital: float,
        symbols: list[str],
    ) -> tuple[list[Trade], list[float]]:
        """백테스트 시뮬레이션 실행"""

        # ❌ 기존 코드 제거
        # trades = []
        # portfolio_values = [initial_capital]
        # current_capital = initial_capital
        # positions = {}

        # ✅ TradeEngine 사용
        from app.models.backtest import BacktestConfig

        config = BacktestConfig(
            name="temp",
            symbols=symbols,
            start_date=datetime.now(),
            end_date=datetime.now(),
            initial_cash=initial_capital,
            commission_rate=0.001,
            slippage_rate=0.0005,
        )

        trade_engine = TradeEngine(config=config)
        portfolio = Portfolio(initial_cash=initial_capital)

        trades = []
        portfolio_values = [portfolio.total_value]

        # ... 시뮬레이션 로직 ...

        for i in range(min_length):
            # 전략 신호 생성
            signals = await strategy_instance.generate_signals(day_data)

            # 신호 실행
            for signal in signals:
                trade = trade_engine.execute_signal(
                    signal=signal,
                    portfolio=portfolio,
                    current_prices=current_prices,
                    timestamp=current_timestamp,
                )

                if trade:
                    trades.append(trade)

            portfolio_values.append(portfolio.total_value)

        return trades, portfolio_values

    # ❌ _execute_trades 메서드 삭제
    # def _execute_trades(self, signals, day_data, positions, current_capital):
    #     ...
```

### 검증 방법

```python
# tests/test_trade_engine.py

import pytest
from app.services.backtest.trade_engine import TradeEngine, Portfolio
from app.models.backtest import BacktestConfig, TradeType, OrderType

@pytest.fixture
def config():
    return BacktestConfig(
        name="test",
        symbols=["AAPL"],
        start_date=datetime.now(),
        end_date=datetime.now(),
        initial_cash=100000.0,
        commission_rate=0.001,
        slippage_rate=0.0005,
    )

@pytest.fixture
def trade_engine(config):
    return TradeEngine(config)

@pytest.fixture
def portfolio():
    return Portfolio(initial_cash=100000.0)

def test_buy_order_execution(trade_engine, portfolio):
    """매수 주문 실행 테스트"""
    # Given
    initial_cash = portfolio.cash

    # When
    trade = trade_engine.execute_order(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.BUY,
        portfolio=portfolio,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is not None
    assert trade.symbol == "AAPL"
    assert trade.quantity == 10
    assert portfolio.cash < initial_cash
    assert portfolio.positions["AAPL"] == 10

def test_insufficient_cash(trade_engine, portfolio):
    """자금 부족 시 거래 실패 테스트"""
    # When
    trade = trade_engine.execute_order(
        symbol="AAPL",
        quantity=1000,
        price=150.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.BUY,
        portfolio=portfolio,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is None  # 거래 실패
    assert portfolio.cash == 100000.0  # 잔액 변동 없음

def test_sell_order_execution(trade_engine, portfolio):
    """매도 주문 실행 테스트"""
    # Given
    # 먼저 매수
    trade_engine.execute_order(
        symbol="AAPL",
        quantity=10,
        price=150.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.BUY,
        portfolio=portfolio,
        timestamp=datetime.now(),
    )

    initial_cash = portfolio.cash

    # When
    trade = trade_engine.execute_order(
        symbol="AAPL",
        quantity=5,
        price=160.0,
        order_type=OrderType.MARKET,
        trade_type=TradeType.SELL,
        portfolio=portfolio,
        timestamp=datetime.now(),
    )

    # Then
    assert trade is not None
    assert portfolio.cash > initial_cash  # 현금 증가
    assert portfolio.positions["AAPL"] == 5  # 포지션 감소
```

---

## P1.3 전략 파라미터 타입 안전성

### 문제 상황

현재 전략 파라미터는 `dict[str, Any]`로 타입 안전성이 없습니다:

```python
# ❌ 현재 방식
class Strategy(BaseDocument):
    parameters: dict[str, Any] = Field(default_factory=dict)

# 런타임 에러 발생 가능
strategy = Strategy(
    name="SMA",
    strategy_type=StrategyType.SMA_CROSSOVER,
    parameters={
        "short_window": "10",  # 문자열! (int 기대)
        "long_windw": 30,      # 오타! (long_window)
    }
)
```

### 개선 방안

#### Step 1: 전략별 Config 클래스 정의

```python
# backend/app/strategies/configs.py

from pydantic import BaseModel, Field, validator
from typing import Optional

class StrategyConfigBase(BaseModel):
    """전략 설정 기본 클래스"""

    # 공통 설정
    lookback_period: int = Field(default=252, ge=30, description="조회 기간 (일)")
    min_data_points: int = Field(default=30, ge=10, description="최소 데이터 포인트")

    # 리스크 관리
    max_position_size: float = Field(default=1.0, ge=0.0, le=1.0)
    stop_loss_pct: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    take_profit_pct: Optional[float] = Field(default=None, ge=0.0)


class SMACrossoverConfig(StrategyConfigBase):
    """SMA 크로스오버 전략 설정"""

    short_window: int = Field(
        default=10,
        ge=2,
        le=50,
        description="단기 이동평균 기간"
    )
    long_window: int = Field(
        default=30,
        ge=10,
        le=200,
        description="장기 이동평균 기간"
    )
    min_crossover_strength: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="최소 교차 강도"
    )

    @validator('long_window')
    def validate_windows(cls, v, values):
        """장기 이평이 단기 이평보다 커야 함"""
        if 'short_window' in values and v <= values['short_window']:
            raise ValueError(
                f"long_window ({v}) must be > short_window ({values['short_window']})"
            )
        return v


class RSIMeanReversionConfig(StrategyConfigBase):
    """RSI 평균회귀 전략 설정"""

    rsi_period: int = Field(
        default=14,
        ge=2,
        le=50,
        description="RSI 계산 기간"
    )
    oversold_threshold: float = Field(
        default=30.0,
        ge=0.0,
        le=50.0,
        description="과매도 임계값"
    )
    overbought_threshold: float = Field(
        default=70.0,
        ge=50.0,
        le=100.0,
        description="과매수 임계값"
    )
    confirmation_periods: int = Field(
        default=2,
        ge=1,
        le=10,
        description="신호 확인 기간"
    )

    @validator('overbought_threshold')
    def validate_thresholds(cls, v, values):
        """과매수 임계값이 과매도 임계값보다 커야 함"""
        if 'oversold_threshold' in values and v <= values['oversold_threshold']:
            raise ValueError(
                f"overbought_threshold ({v}) must be > "
                f"oversold_threshold ({values['oversold_threshold']})"
            )
        return v


class MomentumConfig(StrategyConfigBase):
    """모멘텀 전략 설정"""

    lookback_period: int = Field(
        default=20,
        ge=5,
        le=100,
        description="모멘텀 계산 기간"
    )
    top_n_stocks: int = Field(
        default=5,
        ge=1,
        le=20,
        description="상위 N개 종목 선택"
    )
    rebalance_frequency: str = Field(
        default="monthly",
        description="리밸런싱 주기"
    )

    @validator('rebalance_frequency')
    def validate_frequency(cls, v):
        """리밸런싱 주기 검증"""
        allowed = ['daily', 'weekly', 'monthly', 'quarterly']
        if v not in allowed:
            raise ValueError(f"rebalance_frequency must be one of {allowed}")
        return v


class BuyAndHoldConfig(StrategyConfigBase):
    """바이앤홀드 전략 설정"""

    allocation: dict[str, float] = Field(
        default_factory=dict,
        description="종목별 할당 비율"
    )

    @validator('allocation')
    def validate_allocation(cls, v):
        """할당 비율 검증"""
        if not v:
            return v

        total = sum(v.values())
        if not (0.99 <= total <= 1.01):  # 부동소수점 오차 허용
            raise ValueError(f"Total allocation must be 1.0, got {total}")

        for symbol, ratio in v.items():
            if ratio < 0 or ratio > 1:
                raise ValueError(f"Invalid allocation for {symbol}: {ratio}")

        return v
```

#### Step 2: Strategy 모델 업데이트

```python
# backend/app/models/strategy.py

from typing import Union
from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)

# Config 타입 Union
StrategyConfigUnion = Union[
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
]

class Strategy(BaseDocument):
    """전략 정의 문서 모델"""

    name: str = Field(..., description="전략 이름")
    strategy_type: StrategyType = Field(..., description="전략 타입")
    description: Optional[str] = Field(None, description="전략 설명")

    # ✅ 타입 안전한 설정
    config: StrategyConfigUnion = Field(..., description="전략 설정")

    # ❌ 제거: parameters
    # parameters: dict[str, Any] = Field(default_factory=dict)

    # ... 나머지 필드 ...

    @validator('config')
    def validate_config_type(cls, v, values):
        """설정 타입과 전략 타입 일치 검증"""
        if 'strategy_type' not in values:
            return v

        strategy_type = values['strategy_type']
        config_type = type(v).__name__

        expected_configs = {
            StrategyType.SMA_CROSSOVER: 'SMACrossoverConfig',
            StrategyType.RSI_MEAN_REVERSION: 'RSIMeanReversionConfig',
            StrategyType.MOMENTUM: 'MomentumConfig',
            StrategyType.BUY_AND_HOLD: 'BuyAndHoldConfig',
        }

        expected = expected_configs.get(strategy_type)
        if expected and config_type != expected:
            raise ValueError(
                f"Config type mismatch: {strategy_type} requires "
                f"{expected}, got {config_type}"
            )

        return v
```

#### Step 3: 전략 클래스 업데이트

```python
# backend/app/strategies/sma_crossover.py

from app.strategies.configs import SMACrossoverConfig

class SMACrossoverStrategy(BaseStrategy):
    """SMA 크로스오버 전략"""

    def __init__(self, config: SMACrossoverConfig):  # ✅ 타입 명시
        super().__init__(config)
        self.config: SMACrossoverConfig = config  # 타입 힌트

        # ✅ IDE 자동완성 지원
        logger.info(
            f"SMA Strategy initialized: "
            f"short={self.config.short_window}, "
            f"long={self.config.long_window}"
        )
```

#### Step 4: StrategyService 업데이트

```python
# backend/app/services/strategy_service.py

from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)

class StrategyService:
    # ... 기존 코드 ...

    async def create_strategy(
        self,
        name: str,
        strategy_type: StrategyType,
        config: StrategyConfigUnion,  # ✅ 타입 안전
        description: Optional[str] = None,
        tags: list[str] = None,
        user_id: Optional[str] = None,
    ) -> Strategy:
        """전략 생성 (타입 안전)"""

        # 설정 타입 검증
        expected_configs = {
            StrategyType.SMA_CROSSOVER: SMACrossoverConfig,
            StrategyType.RSI_MEAN_REVERSION: RSIMeanReversionConfig,
            StrategyType.MOMENTUM: MomentumConfig,
            StrategyType.BUY_AND_HOLD: BuyAndHoldConfig,
        }

        expected_config_type = expected_configs.get(strategy_type)
        if expected_config_type and not isinstance(config, expected_config_type):
            raise TypeError(
                f"Invalid config type for {strategy_type}: "
                f"expected {expected_config_type.__name__}, "
                f"got {type(config).__name__}"
            )

        strategy = Strategy(
            name=name,
            strategy_type=strategy_type,
            config=config,  # ✅ Pydantic 검증됨
            description=description or "",
            tags=tags or [],
            user_id=user_id,
        )

        await strategy.insert()
        logger.info(f"Created strategy: {name} ({strategy_type})")
        return strategy

    async def get_strategy_instance(
        self,
        strategy_type: StrategyType,
        config: StrategyConfigUnion,
    ):
        """전략 인스턴스 생성 (타입 안전)"""

        strategy_class = self.strategy_classes.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        # ✅ 타입 체크된 config 전달
        return strategy_class(config=config)
```

#### Step 5: API 스키마 업데이트

```python
# backend/app/schemas/strategy.py

from pydantic import BaseModel
from app.models.strategy import StrategyType
from app.strategies.configs import StrategyConfigUnion

class StrategyCreate(BaseModel):
    """전략 생성 요청"""

    name: str
    strategy_type: StrategyType
    config: StrategyConfigUnion  # ✅ 타입별 검증
    description: Optional[str] = None
    tags: list[str] = []

# 사용 예시
# {
#   "name": "My SMA Strategy",
#   "strategy_type": "sma_crossover",
#   "config": {
#     "short_window": 10,
#     "long_window": 30,
#     "min_crossover_strength": 0.01
#   }
# }
```

### 마이그레이션 스크립트

```python
# backend/scripts/migrate_strategy_parameters.py

"""전략 파라미터를 타입 안전한 config로 마이그레이션"""

import asyncio
from app.models.strategy import Strategy, StrategyType
from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)

async def migrate_strategies():
    """기존 전략 마이그레이션"""

    strategies = await Strategy.find_all().to_list()

    for strategy in strategies:
        if hasattr(strategy, 'parameters') and strategy.parameters:
            # parameters -> config 변환
            config = _convert_parameters_to_config(
                strategy.strategy_type,
                strategy.parameters,
            )

            if config:
                strategy.config = config
                delattr(strategy, 'parameters')  # parameters 필드 제거
                await strategy.save()
                print(f"Migrated: {strategy.name}")
        else:
            print(f"Skipped: {strategy.name} (no parameters)")

def _convert_parameters_to_config(
    strategy_type: StrategyType,
    parameters: dict,
):
    """파라미터를 Config 객체로 변환"""

    if strategy_type == StrategyType.SMA_CROSSOVER:
        return SMACrossoverConfig(**parameters)
    elif strategy_type == StrategyType.RSI_MEAN_REVERSION:
        return RSIMeanReversionConfig(**parameters)
    elif strategy_type == StrategyType.MOMENTUM:
        return MomentumConfig(**parameters)
    elif strategy_type == StrategyType.BUY_AND_HOLD:
        return BuyAndHoldConfig(**parameters)
    else:
        print(f"Unknown strategy type: {strategy_type}")
        return None

if __name__ == "__main__":
    asyncio.run(migrate_strategies())
```

### 검증 방법

```python
# tests/test_strategy_config.py

import pytest
from pydantic import ValidationError
from app.strategies.configs import SMACrossoverConfig, RSIMeanReversionConfig

def test_sma_config_validation():
    """SMA 설정 검증 테스트"""

    # ✅ 유효한 설정
    config = SMACrossoverConfig(
        short_window=10,
        long_window=30,
    )
    assert config.short_window == 10
    assert config.long_window == 30

    # ❌ 잘못된 설정 (long < short)
    with pytest.raises(ValidationError) as exc_info:
        SMACrossoverConfig(
            short_window=30,
            long_window=10,
        )
    assert "must be >" in str(exc_info.value)

    # ❌ 타입 오류
    with pytest.raises(ValidationError):
        SMACrossoverConfig(
            short_window="10",  # 문자열
            long_window=30,
        )

def test_rsi_config_validation():
    """RSI 설정 검증 테스트"""

    # ✅ 유효한 설정
    config = RSIMeanReversionConfig(
        rsi_period=14,
        oversold_threshold=30.0,
        overbought_threshold=70.0,
    )
    assert config.oversold_threshold < config.overbought_threshold

    # ❌ 잘못된 임계값
    with pytest.raises(ValidationError):
        RSIMeanReversionConfig(
            oversold_threshold=70.0,
            overbought_threshold=30.0,  # 역전
        )
```

---

## 테스트 전략

### 단위 테스트

```bash
# 개별 테스트 실행
cd backend
uv run pytest tests/test_trade_engine.py -v
uv run pytest tests/test_strategy_config.py -v
uv run pytest tests/test_service_factory.py -v
```

### 통합 테스트

```python
# tests/integration/test_backtest_flow.py

async def test_complete_backtest_flow():
    """전체 백테스트 흐름 테스트"""

    # 1. 전략 생성
    config = SMACrossoverConfig(short_window=10, long_window=30)
    strategy = await strategy_service.create_strategy(
        name="Test SMA",
        strategy_type=StrategyType.SMA_CROSSOVER,
        config=config,
    )

    # 2. 백테스트 생성
    backtest_config = BacktestConfig(
        name="Test Backtest",
        symbols=["AAPL"],
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        initial_cash=100000.0,
    )

    backtest = await backtest_service.create_backtest(
        name="Test",
        config=backtest_config,
    )

    # 3. 백테스트 실행
    result = await backtest_service.execute_backtest(
        backtest_id=str(backtest.id),
        strategy_id=str(strategy.id),
    )

    # 4. 결과 검증
    assert result is not None
    assert result.performance.total_return is not None
    assert len(result.trades) > 0
```

### 성능 테스트

```python
# tests/performance/test_trade_engine_performance.py

import time

def test_trade_engine_performance():
    """거래 엔진 성능 테스트"""

    trade_engine = TradeEngine(config)
    portfolio = Portfolio(initial_cash=1000000.0)

    # 10,000회 거래 시뮬레이션
    start = time.time()

    for i in range(10000):
        trade_engine.execute_order(
            symbol="AAPL",
            quantity=10,
            price=150.0 + (i % 100),
            order_type=OrderType.MARKET,
            trade_type=TradeType.BUY if i % 2 == 0 else TradeType.SELL,
            portfolio=portfolio,
            timestamp=datetime.now(),
        )

    elapsed = time.time() - start

    print(f"10,000 trades in {elapsed:.2f}s")
    print(f"Throughput: {10000/elapsed:.0f} trades/sec")

    assert elapsed < 1.0  # 1초 이내 완료
```

---

## 배포 체크리스트

### Phase 1 배포 전 체크

- [x] **의존성 주입 개선**

  - [x] `BacktestService` 생성자 업데이트
    - 필수 파라미터로 변경, 초기화 시 즉시 IntegratedBacktestExecutor 생성
  - [x] `ServiceFactory` 수정
    - 이미 올바르게 구현됨 (변경 불필요)
  - [x] `set_dependencies` 메서드 제거
    - BacktestService에서 완전히 제거됨
  - [x] `main.py` lifespan 업데이트
    - 이미 올바르게 구현됨 (변경 불필요)
  - [x] 단위 테스트 통과
    - test_service_factory.py 생성 및 통과 (3/3 tests)

- [x] **거래 로직 통합**

  - [x] `TradeEngine` 클래스 구현
    - Portfolio, TradeCosts 포함, 완전한 구현
  - [x] `Portfolio` 클래스 구현
    - 포지션 관리, 평균 단가 계산
  - [x] `TradingSimulator` 제거
    - BacktestService에서 완전히 제거
  - [x] `IntegratedBacktestExecutor` 업데이트
    - TradeEngine 사용, \_execute_trades 메서드 제거
  - [x] 통합 테스트 통과
    - test_trade_engine.py 생성 및 통과 (6/6 tests)

- [x] **전략 파라미터 타입 안전성**

  - [x] Config 클래스 정의 (4개 전략)
    - StrategyConfigBase, SMACrossover, RSI, Momentum, BuyAndHold 완성
  - [x] `Strategy` 모델 업데이트
    - parameters -> config (StrategyConfigUnion)
  - [x] 전략 클래스 업데이트
    - SMA, RSI, Momentum, BuyAndHold 모두 configs 사용
  - [x] `StrategyService` 업데이트
    - get_strategy_instance에서 타입 안전 config 사용
  - [x] API 스키마 업데이트
    - StrategyCreate, StrategyUpdate, TemplateCreate 등 모두 config 필드로 변경
  - [x] 단위 테스트 통과
    - test_strategy_config.py 생성 및 통과 (3/3 tests)

- [x] **문서화**
  - [x] CHANGELOG 작성
    - CHANGELOG.md 생성 (Phase 1 모든 변경사항 문서화)

### 배포 단계

1. **스테이징 배포**

   ```bash
   # 마이그레이션 실행
   uv run python scripts/migrate_strategy_parameters.py

   # 서비스 재시작
   pnpm dev:backend

   # 통합 테스트
   uv run pytest tests/integration/ -v
   ```

2. **프로덕션 배포**

   ```bash
   # 백업
   mongodump --uri="mongodb://localhost:27019" --out=backup_$(date +%Y%m%d)

   # 마이그레이션
   uv run python scripts/migrate_strategy_parameters.py

   # 배포
   docker-compose up -d backend

   # 검증
   curl http://localhost:8500/health
   ```

3. **롤백 계획**

   ```bash
   # 백업 복원
   mongorestore --uri="mongodb://localhost:27019" backup_20251013/

   # 이전 버전 배포
   git checkout <previous-commit>
   docker-compose up -d backend
   ```

---

**다음 단계**: [Phase 2 구현 가이드](./REFACTORING_PHASE2.md) 참조
