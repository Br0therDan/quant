# Strategy & Backtest 리팩토링 Phase 2

> **Phase 2 구현 가이드**: 레이어드 아키텍처 도입 (2-3주)  
> **목표**: 책임 분리, 확장 가능한 구조, 비동기 최적화

## 📋 목차

1. [P2.1 BacktestOrchestrator 분리](#p21-backtestorchestrator-분리)
2. [P2.2 StrategyExecutor 분리](#p22-strategyexecutor-분리)
3. [P2.3 PerformanceAnalyzer 분리](#p23-performanceanalyzer-분리)
4. [P2.4 DataProcessor 도입](#p24-dataprocessor-도입)
5. [테스트 전략](#테스트-전략)
6. [배포 체크리스트](#배포-체크리스트)

---

## 개요

### Phase 1 완료 사항 (기반)

✅ 의존성 주입 완료 (ServiceFactory)  
✅ 거래 로직 통합 (TradeEngine)  
✅ 타입 안전성 확보 (Config 클래스)  
✅ 12/12 테스트 통과

### Phase 2 목표

🎯 **책임 분리**: 707줄의 BacktestService를 5개 컴포넌트로 분리  
🎯 **비동기 최적화**: 병렬 데이터 수집 및 처리  
🎯 **확장성**: 새로운 전략/지표 추가 용이  
🎯 **테스트 용이성**: 각 컴포넌트 독립 테스트 가능

### 아키텍처 변경

```
Before (Phase 1):
BacktestService (707 lines)
├── CRUD 로직
├── 실행 로직
├── 성과 계산
├── DuckDB 저장
└── 데이터 수집

After (Phase 2):
BacktestService (CRUD only, ~150 lines)
└── BacktestOrchestrator (~200 lines)
    ├── StrategyExecutor (~150 lines)
    ├── TradeEngine (✅ 완료)
    ├── PerformanceAnalyzer (~200 lines)
    └── DataProcessor (~150 lines)
```

---

## P2.1 BacktestOrchestrator 분리

### 목표

백테스트 실행 워크플로우를 조율하는 독립 컴포넌트 생성

### 책임

1. 백테스트 전체 파이프라인 관리
2. 상태 추적 및 업데이트
3. 오류 처리 및 복구
4. 결과 취합 및 저장

### 구현

#### Step 1: BacktestOrchestrator 클래스 생성

**파일**: `backend/app/services/backtest/orchestrator.py` (NEW)

```python
"""
백테스트 워크플로우 조율자
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from beanie import PydanticObjectId

from app.models.backtest import (
    Backtest,
    BacktestResult,
    BacktestStatus,
    BacktestExecution,
)
from app.services.backtest.executor import StrategyExecutor
from app.services.backtest.trade_engine import TradeEngine
from app.services.backtest.performance import PerformanceAnalyzer
from app.services.backtest.data_processor import DataProcessor
from app.services.market_data_service import MarketDataService

logger = logging.getLogger(__name__)


class BacktestOrchestrator:
    """백테스트 워크플로우 조율자

    Orchestrator 패턴을 사용하여 백테스트 실행 파이프라인을 관리합니다.
    각 단계는 독립적인 컴포넌트가 처리하며, Orchestrator는 워크플로우만 조율합니다.
    """

    def __init__(
        self,
        market_data_service: MarketDataService,
        strategy_executor: StrategyExecutor,
        trade_engine: TradeEngine,
        performance_analyzer: PerformanceAnalyzer,
        data_processor: DataProcessor,
    ):
        self.market_data = market_data_service
        self.strategy_executor = strategy_executor
        self.trade_engine = trade_engine
        self.performance = performance_analyzer
        self.data_processor = data_processor

    async def execute_backtest(
        self,
        backtest_id: str,
    ) -> Optional[BacktestResult]:
        """백테스트 실행 파이프라인

        Workflow:
        1. 백테스트 조회 및 검증
        2. 상태 업데이트 (PENDING → RUNNING)
        3. 시장 데이터 수집 및 정제
        4. 전략 신호 생성
        5. 거래 시뮬레이션
        6. 성과 분석
        7. 결과 저장 및 상태 업데이트 (RUNNING → COMPLETED)

        Args:
            backtest_id: 백테스트 ID

        Returns:
            BacktestResult 또는 None (실패 시)
        """
        start_time = datetime.now(timezone.utc)
        backtest = None

        try:
            # 1. 백테스트 조회 및 검증
            backtest = await Backtest.get(PydanticObjectId(backtest_id))
            if not backtest:
                logger.error(f"Backtest not found: {backtest_id}")
                return None

            # 2. 상태 업데이트
            await self._update_status(backtest, BacktestStatus.RUNNING, start_time)

            # 3. 시장 데이터 수집 및 정제
            logger.info(f"[{backtest_id}] Step 1: Collecting market data")
            market_data = await self._collect_and_process_data(backtest)

            if not market_data:
                raise ValueError("No market data collected")

            # 4. 전략 신호 생성
            logger.info(f"[{backtest_id}] Step 2: Generating strategy signals")
            signals = await self.strategy_executor.generate_signals(
                strategy_id=backtest.strategy_id,
                market_data=market_data,
                config=backtest.config,
            )

            # 5. 거래 시뮬레이션
            logger.info(f"[{backtest_id}] Step 3: Simulating trades")
            trades, portfolio_values = await self._simulate_trades(
                signals=signals,
                market_data=market_data,
                initial_capital=backtest.config.initial_cash,
                config=backtest.config,
            )

            # 6. 성과 분석
            logger.info(f"[{backtest_id}] Step 4: Analyzing performance")
            metrics = await self.performance.calculate_metrics(
                portfolio_values=portfolio_values,
                trades=trades,
                initial_capital=backtest.config.initial_cash,
                benchmark_returns=None,  # TODO: 벤치마크 추가
            )

            # 7. 결과 저장
            logger.info(f"[{backtest_id}] Step 5: Saving results")
            result = await self._save_result(
                backtest=backtest,
                trades=trades,
                portfolio_values=portfolio_values,
                metrics=metrics,
                start_time=start_time,
            )

            # 8. 상태 업데이트
            await self._update_status(
                backtest, BacktestStatus.COMPLETED, start_time, datetime.now(timezone.utc)
            )

            logger.info(f"[{backtest_id}] Backtest completed successfully")
            return result

        except Exception as e:
            logger.error(f"[{backtest_id}] Backtest failed: {e}", exc_info=True)

            if backtest:
                await self._update_status(
                    backtest,
                    BacktestStatus.FAILED,
                    start_time,
                    datetime.now(timezone.utc),
                    error_message=str(e),
                )

            return None

    async def _collect_and_process_data(
        self, backtest: Backtest
    ) -> dict[str, Any]:
        """시장 데이터 수집 및 정제"""
        raw_data = {}

        # 병렬 데이터 수집
        tasks = [
            self.market_data.get_stock_data(
                symbol=symbol,
                start_date=backtest.config.start_date,
                end_date=backtest.config.end_date,
            )
            for symbol in backtest.config.symbols
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, result in zip(backtest.config.symbols, results):
            if isinstance(result, Exception):
                logger.warning(f"Failed to collect data for {symbol}: {result}")
                continue

            if result is not None:
                raw_data[symbol] = result

        if not raw_data:
            return {}

        # 데이터 정제 및 검증
        processed_data = await self.data_processor.process_market_data(
            raw_data=raw_data,
            required_columns=["open", "high", "low", "close", "volume"],
            min_data_points=backtest.config.get("min_data_points", 30),
        )

        return processed_data

    async def _simulate_trades(
        self,
        signals: list,
        market_data: dict,
        initial_capital: float,
        config: Any,
    ) -> tuple[list, list]:
        """거래 시뮬레이션"""
        # TradeEngine 사용 (Phase 1에서 구현 완료)
        portfolio_values = []
        trades = []

        # TODO: TradeEngine.execute_signals 메서드로 통합
        for signal in signals:
            trade = await self.trade_engine.execute_signal(
                signal=signal,
                market_data=market_data,
                config=config,
            )

            if trade:
                trades.append(trade)

            # 포트폴리오 가치 계산
            portfolio_value = self.trade_engine.portfolio.get_total_value(
                current_prices={s: market_data[s]["close"][-1] for s in config.symbols}
            )
            portfolio_values.append(portfolio_value)

        return trades, portfolio_values

    async def _save_result(
        self,
        backtest: Backtest,
        trades: list,
        portfolio_values: list,
        metrics: dict,
        start_time: datetime,
    ) -> BacktestResult:
        """백테스트 결과 저장"""
        result = BacktestResult(
            backtest_id=str(backtest.id),
            start_time=start_time,
            end_time=datetime.now(timezone.utc),
            status=BacktestStatus.COMPLETED,
            trades=trades,
            portfolio_values=portfolio_values,
            metrics=metrics,
        )

        await result.insert()
        return result

    async def _update_status(
        self,
        backtest: Backtest,
        status: BacktestStatus,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """백테스트 상태 업데이트"""
        backtest.status = status
        backtest.start_time = start_time

        if end_time:
            backtest.end_time = end_time
            backtest.duration_seconds = (end_time - start_time).total_seconds()

        if error_message:
            backtest.error_message = error_message

        await backtest.save()
```

#### Step 2: BacktestService 리팩토링

**파일**: `backend/app/services/backtest_service.py` (REFACTOR)

```python
"""
백테스트 서비스 - CRUD 및 조회만 담당
"""

from typing import Optional, List
from beanie import PydanticObjectId

from app.models.backtest import Backtest, BacktestConfig, BacktestStatus
from app.services.backtest.orchestrator import BacktestOrchestrator


class BacktestService:
    """백테스트 CRUD 서비스

    Phase 2 변경사항:
    - 실행 로직 제거 → BacktestOrchestrator로 이동
    - CRUD 및 조회 기능만 유지
    - 단일 책임 원칙 준수
    """

    def __init__(self, orchestrator: BacktestOrchestrator):
        self.orchestrator = orchestrator

    async def create_backtest(
        self,
        name: str,
        description: str,
        strategy_id: str,
        config: BacktestConfig,
        user_id: Optional[str] = None,
    ) -> Backtest:
        """백테스트 생성"""
        backtest = Backtest(
            name=name,
            description=description,
            strategy_id=strategy_id,
            config=config,
            status=BacktestStatus.PENDING,
            user_id=user_id,
        )

        await backtest.insert()
        return backtest

    async def get_backtest(self, backtest_id: str) -> Optional[Backtest]:
        """백테스트 조회"""
        return await Backtest.get(PydanticObjectId(backtest_id))

    async def list_backtests(
        self,
        user_id: Optional[str] = None,
        strategy_id: Optional[str] = None,
        status: Optional[BacktestStatus] = None,
        limit: int = 50,
    ) -> List[Backtest]:
        """백테스트 목록 조회"""
        query = {}

        if user_id:
            query["user_id"] = user_id
        if strategy_id:
            query["strategy_id"] = strategy_id
        if status:
            query["status"] = status

        return await Backtest.find(query).limit(limit).to_list()

    async def execute_backtest(self, backtest_id: str):
        """백테스트 실행 (Orchestrator에 위임)"""
        return await self.orchestrator.execute_backtest(backtest_id)

    async def delete_backtest(self, backtest_id: str) -> bool:
        """백테스트 삭제"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return False

        await backtest.delete()
        return True
```

#### Step 3: ServiceFactory 업데이트

**파일**: `backend/app/services/service_factory.py` (UPDATE)

```python
# 추가 임포트
from app.services.backtest.orchestrator import BacktestOrchestrator
from app.services.backtest.executor import StrategyExecutor
from app.services.backtest.performance import PerformanceAnalyzer
from app.services.backtest.data_processor import DataProcessor

class ServiceFactory:
    # ... 기존 코드 ...

    def get_backtest_orchestrator(self) -> BacktestOrchestrator:
        """BacktestOrchestrator 싱글톤 생성"""
        if self._backtest_orchestrator is None:
            self._backtest_orchestrator = BacktestOrchestrator(
                market_data_service=self.get_market_data_service(),
                strategy_executor=self.get_strategy_executor(),
                trade_engine=self.get_trade_engine(),
                performance_analyzer=self.get_performance_analyzer(),
                data_processor=self.get_data_processor(),
            )
        return self._backtest_orchestrator

    def get_backtest_service(self) -> BacktestService:
        """BacktestService 싱글톤 생성 (리팩토링)"""
        if self._backtest_service is None:
            self._backtest_service = BacktestService(
                orchestrator=self.get_backtest_orchestrator()
            )
        return self._backtest_service
```

### 체크리스트

- [ ] `backend/app/services/backtest/orchestrator.py` 생성
- [ ] `BacktestOrchestrator` 클래스 구현
- [ ] `BacktestService` 리팩토링 (CRUD only)
- [ ] `ServiceFactory` 업데이트
- [ ] 테스트 작성: `tests/test_orchestrator.py`
- [ ] 기존 테스트 통과 확인

---

## P2.2 StrategyExecutor 분리

### 목표

전략 신호 생성 로직을 독립 컴포넌트로 분리

### 책임

1. 전략 인스턴스 생성
2. 시장 데이터 전처리
3. 지표 계산
4. 신호 생성

### 구현

#### Step 1: StrategyExecutor 클래스 생성

**파일**: `backend/app/services/backtest/executor.py` (NEW)

```python
"""
전략 실행기 - 전략 신호 생성 담당
"""

import logging
from typing import Any, Dict, List, Optional

from app.models.strategy import Strategy, StrategyType
from app.services.strategy_service import StrategyService
from app.strategies.base_strategy import BaseStrategy

logger = logging.getLogger(__name__)


class StrategyExecutor:
    """전략 실행기

    전략 인스턴스를 생성하고 시장 데이터를 기반으로 매매 신호를 생성합니다.
    """

    def __init__(self, strategy_service: StrategyService):
        self.strategy_service = strategy_service

    async def generate_signals(
        self,
        strategy_id: str,
        market_data: Dict[str, Any],
        config: Any,
    ) -> List[Dict[str, Any]]:
        """전략 신호 생성

        Args:
            strategy_id: 전략 ID
            market_data: 시장 데이터 딕셔너리
            config: 백테스트 설정

        Returns:
            생성된 신호 리스트
        """
        # 1. 전략 조회
        strategy = await self.strategy_service.get_strategy(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy not found: {strategy_id}")

        # 2. 전략 인스턴스 생성
        strategy_instance = await self.strategy_service.get_strategy_instance(
            strategy_type=strategy.strategy_type,
            config=strategy.config,
        )

        if not strategy_instance:
            raise ValueError(f"Failed to create strategy instance: {strategy.strategy_type}")

        # 3. 전략 초기화
        strategy_instance.initialize(market_data)

        # 4. 지표 계산
        indicators = await self._calculate_indicators(strategy_instance, market_data)

        # 5. 신호 생성
        signals = strategy_instance.generate_signals(market_data)

        logger.info(
            f"Generated {len(signals)} signals for strategy {strategy.name} "
            f"({strategy.strategy_type})"
        )

        return signals

    async def _calculate_indicators(
        self,
        strategy: BaseStrategy,
        market_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """기술적 지표 계산

        전략에 필요한 지표를 계산합니다.
        """
        indicators = {}

        try:
            # 전략별 지표 계산
            strategy_indicators = strategy.calculate_indicators(market_data)
            indicators.update(strategy_indicators)

        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
            raise

        return indicators

    async def validate_signals(
        self,
        signals: List[Dict[str, Any]],
        market_data: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """신호 검증

        생성된 신호를 검증하고 필터링합니다.
        """
        valid_signals = []

        for signal in signals:
            # 기본 검증
            if not all(k in signal for k in ["symbol", "signal_type", "price"]):
                logger.warning(f"Invalid signal format: {signal}")
                continue

            # 가격 검증
            if signal["price"] <= 0:
                logger.warning(f"Invalid price in signal: {signal}")
                continue

            valid_signals.append(signal)

        logger.info(f"Validated {len(valid_signals)}/{len(signals)} signals")
        return valid_signals
```

### 체크리스트

- [ ] `backend/app/services/backtest/executor.py` 생성
- [ ] `StrategyExecutor` 클래스 구현
- [ ] `BacktestOrchestrator`에 통합
- [ ] 테스트 작성: `tests/test_strategy_executor.py`

---

## P2.3 PerformanceAnalyzer 분리

### 목표

성과 분석 로직을 독립 컴포넌트로 분리

### 책임

1. 수익률 계산
2. 리스크 지표 계산 (변동성, Sharpe Ratio, MDD)
3. 거래 통계 분석
4. 벤치마크 비교

### 구현

**파일**: `backend/app/services/backtest/performance.py` (NEW)

```python
"""
성과 분석기 - 백테스트 성과 지표 계산
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from app.models.backtest import PerformanceMetrics, Trade

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """성과 분석기

    백테스트 결과를 분석하여 다양한 성과 지표를 계산합니다.
    """

    async def calculate_metrics(
        self,
        portfolio_values: List[float],
        trades: List[Trade],
        initial_capital: float,
        benchmark_returns: Optional[List[float]] = None,
    ) -> PerformanceMetrics:
        """성과 지표 계산

        Args:
            portfolio_values: 포트폴리오 가치 시계열
            trades: 거래 내역
            initial_capital: 초기 자본
            benchmark_returns: 벤치마크 수익률 (선택)

        Returns:
            PerformanceMetrics 객체
        """
        if not portfolio_values:
            return self._empty_metrics()

        # 수익률 계산
        returns = self._calculate_returns(portfolio_values)

        # 기본 지표
        total_return = (portfolio_values[-1] - initial_capital) / initial_capital
        annualized_return = self._annualize_return(total_return, len(portfolio_values))

        # 리스크 지표
        volatility = np.std(returns) * np.sqrt(252) if returns else 0.0
        sharpe_ratio = self._calculate_sharpe_ratio(returns)
        max_drawdown = self._calculate_max_drawdown(portfolio_values)

        # 거래 통계
        trade_stats = self._analyze_trades(trades)

        return PerformanceMetrics(
            total_return=round(total_return, 4),
            annualized_return=round(annualized_return, 4),
            volatility=round(volatility, 4),
            sharpe_ratio=round(sharpe_ratio, 4),
            max_drawdown=round(max_drawdown, 4),
            total_trades=trade_stats["total_trades"],
            winning_trades=trade_stats["winning_trades"],
            losing_trades=trade_stats["losing_trades"],
            win_rate=round(trade_stats["win_rate"], 4),
            avg_win=round(trade_stats["avg_win"], 4),
            avg_loss=round(trade_stats["avg_loss"], 4),
            profit_factor=round(trade_stats["profit_factor"], 4),
        )

    def _calculate_returns(self, portfolio_values: List[float]) -> np.ndarray:
        """수익률 계산"""
        if len(portfolio_values) < 2:
            return np.array([])

        values = np.array(portfolio_values)
        returns = np.diff(values) / values[:-1]
        return returns

    def _annualize_return(self, total_return: float, periods: int) -> float:
        """연율화 수익률 계산"""
        if periods <= 0:
            return 0.0

        years = periods / 252  # 거래일 기준
        if years <= 0:
            return 0.0

        return (1 + total_return) ** (1 / years) - 1

    def _calculate_sharpe_ratio(
        self, returns: np.ndarray, risk_free_rate: float = 0.02
    ) -> float:
        """샤프 비율 계산"""
        if len(returns) == 0:
            return 0.0

        excess_returns = returns - (risk_free_rate / 252)

        if np.std(excess_returns) == 0:
            return 0.0

        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)

    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """최대 낙폭 계산"""
        if not portfolio_values:
            return 0.0

        values = np.array(portfolio_values)
        cummax = np.maximum.accumulate(values)
        drawdowns = (values - cummax) / cummax

        return float(np.min(drawdowns))

    def _analyze_trades(self, trades: List[Trade]) -> Dict[str, Any]:
        """거래 통계 분석"""
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
            }

        # 거래별 손익 계산
        pnls = []
        for trade in trades:
            # 간단한 손익 계산 (실제로는 매수/매도 매칭 필요)
            pnl = trade.price * trade.quantity
            pnls.append(pnl)

        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p < 0]

        return {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": len(wins) / len(trades) if trades else 0.0,
            "avg_win": np.mean(wins) if wins else 0.0,
            "avg_loss": np.mean(losses) if losses else 0.0,
            "profit_factor": (
                sum(wins) / abs(sum(losses)) if losses and sum(losses) != 0 else 0.0
            ),
        }

    def _empty_metrics(self) -> PerformanceMetrics:
        """빈 메트릭 반환"""
        return PerformanceMetrics(
            total_return=0.0,
            annualized_return=0.0,
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
        )
```

### 체크리스트

- [ ] `backend/app/services/backtest/performance.py` 생성
- [ ] `PerformanceAnalyzer` 클래스 구현
- [ ] `BacktestOrchestrator`에 통합
- [ ] 테스트 작성: `tests/test_performance_analyzer.py`

---

## P2.4 DataProcessor 도입

### 목표

데이터 정제 및 검증 로직을 독립 컴포넌트로 분리

### 책임

1. 시장 데이터 검증
2. 결측치 처리
3. 데이터 정규화
4. 이상치 탐지

### 구현

**파일**: `backend/app/services/backtest/data_processor.py` (NEW)

```python
"""
데이터 처리기 - 시장 데이터 정제 및 검증
"""

import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessor:
    """데이터 처리기

    시장 데이터를 정제하고 검증합니다.
    """

    async def process_market_data(
        self,
        raw_data: Dict[str, Any],
        required_columns: List[str],
        min_data_points: int = 30,
    ) -> Dict[str, pd.DataFrame]:
        """시장 데이터 처리

        Args:
            raw_data: 원시 시장 데이터
            required_columns: 필수 컬럼 리스트
            min_data_points: 최소 데이터 포인트 수

        Returns:
            처리된 데이터 딕셔너리
        """
        processed = {}

        for symbol, data in raw_data.items():
            try:
                # 1. DataFrame 변환
                df = self._to_dataframe(data)

                # 2. 필수 컬럼 검증
                if not self._validate_columns(df, required_columns):
                    logger.warning(f"Missing required columns for {symbol}")
                    continue

                # 3. 최소 데이터 포인트 검증
                if len(df) < min_data_points:
                    logger.warning(
                        f"Insufficient data points for {symbol}: {len(df)} < {min_data_points}"
                    )
                    continue

                # 4. 결측치 처리
                df = self._handle_missing_values(df)

                # 5. 이상치 탐지 및 처리
                df = self._handle_outliers(df)

                # 6. 데이터 정렬
                df = df.sort_index()

                processed[symbol] = df

            except Exception as e:
                logger.error(f"Failed to process data for {symbol}: {e}")
                continue

        logger.info(f"Successfully processed {len(processed)}/{len(raw_data)} symbols")
        return processed

    def _to_dataframe(self, data: Any) -> pd.DataFrame:
        """데이터를 DataFrame으로 변환"""
        if isinstance(data, pd.DataFrame):
            return data
        elif isinstance(data, dict):
            return pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")

    def _validate_columns(self, df: pd.DataFrame, required: List[str]) -> bool:
        """필수 컬럼 검증"""
        return all(col in df.columns for col in required)

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """결측치 처리

        전진 채움(forward fill) 방식 사용
        """
        return df.fillna(method="ffill").fillna(method="bfill")

    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """이상치 처리

        IQR 방식으로 이상치 탐지 및 제한
        """
        for col in ["open", "high", "low", "close"]:
            if col not in df.columns:
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 3 * IQR
            upper_bound = Q3 + 3 * IQR

            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

        return df

    async def validate_data_quality(
        self, data: pd.DataFrame
    ) -> Dict[str, Any]:
        """데이터 품질 검증

        Returns:
            품질 지표 딕셔너리
        """
        return {
            "total_rows": len(data),
            "missing_values": data.isnull().sum().to_dict(),
            "date_range": {
                "start": str(data.index.min()),
                "end": str(data.index.max()),
            },
            "columns": list(data.columns),
        }
```

### 체크리스트

- [ ] `backend/app/services/backtest/data_processor.py` 생성
- [ ] `DataProcessor` 클래스 구현
- [ ] `BacktestOrchestrator`에 통합
- [ ] 테스트 작성: `tests/test_data_processor.py`

---

## 테스트 전략

### 1. 단위 테스트 (Unit Tests)

각 컴포넌트를 독립적으로 테스트합니다.

```python
# tests/test_orchestrator.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.backtest.orchestrator import BacktestOrchestrator


@pytest.mark.asyncio
async def test_orchestrator_execute_success():
    """백테스트 실행 성공 시나리오"""
    # Arrange
    mock_market_data = AsyncMock()
    mock_strategy_executor = AsyncMock()
    mock_trade_engine = MagicMock()
    mock_performance = AsyncMock()
    mock_data_processor = AsyncMock()

    orchestrator = BacktestOrchestrator(
        market_data_service=mock_market_data,
        strategy_executor=mock_strategy_executor,
        trade_engine=mock_trade_engine,
        performance_analyzer=mock_performance,
        data_processor=mock_data_processor,
    )

    # Mock 응답 설정
    mock_data_processor.process_market_data.return_value = {"AAPL": mock_df}
    mock_strategy_executor.generate_signals.return_value = [mock_signal]
    mock_performance.calculate_metrics.return_value = mock_metrics

    # Act
    result = await orchestrator.execute_backtest("test_backtest_id")

    # Assert
    assert result is not None
    assert result.status == BacktestStatus.COMPLETED
    mock_data_processor.process_market_data.assert_called_once()
    mock_strategy_executor.generate_signals.assert_called_once()


@pytest.mark.asyncio
async def test_orchestrator_execute_failure():
    """백테스트 실행 실패 시나리오"""
    # Arrange
    orchestrator = create_orchestrator_with_failing_data_processor()

    # Act
    result = await orchestrator.execute_backtest("test_backtest_id")

    # Assert
    assert result is None  # 실패 시 None 반환
```

### 2. 통합 테스트 (Integration Tests)

여러 컴포넌트가 함께 작동하는지 테스트합니다.

```python
# tests/integration/test_backtest_pipeline.py
@pytest.mark.asyncio
async def test_full_backtest_pipeline():
    """전체 백테스트 파이프라인 테스트"""
    # 실제 DB 연결, 실제 서비스 사용
    service_factory = ServiceFactory()
    backtest_service = service_factory.get_backtest_service()

    # 백테스트 생성
    backtest = await backtest_service.create_backtest(
        name="Integration Test",
        strategy_id=test_strategy_id,
        config=test_config,
    )

    # 실행
    result = await backtest_service.execute_backtest(str(backtest.id))

    # 검증
    assert result is not None
    assert len(result.trades) > 0
    assert result.metrics.total_return != 0.0
```

### 3. 성능 테스트

```python
# tests/performance/test_orchestrator_performance.py
@pytest.mark.benchmark
def test_orchestrator_performance(benchmark):
    """Orchestrator 성능 테스트"""
    result = benchmark(run_backtest_sync, large_dataset)

    # 성능 기준: 1000개 데이터 포인트를 5초 이내 처리
    assert result.duration < 5.0
```

### 테스트 실행

```bash
# 단위 테스트
cd backend && uv run pytest tests/test_orchestrator.py -v

# 통합 테스트
cd backend && uv run pytest tests/integration/ -v

# 전체 테스트
cd backend && uv run pytest -v

# 커버리지 확인
cd backend && uv run pytest --cov=app/services/backtest --cov-report=html
```

---

## 배포 체크리스트

### 코드 품질

- [ ] 모든 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] 코드 커버리지 80% 이상
- [ ] Ruff 린트 통과
- [ ] 타입 체크 통과 (Pyright)

### 문서화

- [ ] 각 클래스에 docstring 작성
- [ ] API 문서 업데이트
- [ ] CHANGELOG.md 업데이트
- [ ] README.md 업데이트

### 성능

- [ ] 백테스트 실행 시간 < 5초 (1000 데이터 포인트 기준)
- [ ] 메모리 사용량 < 500MB
- [ ] API 응답 시간 < 200ms

### 마이그레이션

- [ ] 기존 백테스트 데이터 호환성 확인
- [ ] ServiceFactory 업데이트
- [ ] API 라우터 업데이트 (필요 시)

---

## Phase 2 완료 기준

✅ **코드 분리 완료**

- [ ] BacktestOrchestrator 구현
- [ ] StrategyExecutor 구현
- [ ] PerformanceAnalyzer 구현
- [ ] DataProcessor 구현

✅ **테스트 통과**

- [ ] 20개 이상의 단위 테스트 작성 및 통과
- [ ] 5개 이상의 통합 테스트 통과

✅ **성능 개선**

- [ ] 병렬 데이터 수집으로 30% 이상 속도 향상

✅ **문서화**

- [ ] 모든 공개 API에 docstring 작성
- [ ] 아키텍처 다이어그램 업데이트

---

## 다음 단계 (Phase 3)

Phase 2 완료 후 진행할 내용:

1. **리스크 관리 강화**

   - 포지션 사이징 알고리즘
   - 동적 손절/익절
   - 포트폴리오 최적화

2. **고급 분석 기능**

   - 몬테카를로 시뮬레이션
   - 워크 포워드 분석
   - 매개변수 최적화

3. **실시간 모니터링**
   - WebSocket 기반 진행 상황 스트리밍
   - 대시보드 통합
   - 알림 시스템

---

**작성일**: 2025-10-13  
**Phase 2 예상 소요 시간**: 2-3주  
**현재 상태**: 🟡 작성 완료, 구현 시작 대기
