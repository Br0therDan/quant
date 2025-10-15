"""
Stock Data Coverage Management
데이터 커버리지 메타데이터 관리
"""

from typing import List, Literal, Sequence
from datetime import datetime, timedelta, timezone
import logging

from app.models.market_data.stock import (
    DailyPrice,
    WeeklyPrice,
    MonthlyPrice,
    StockDataCoverage,
)
from .base import BaseStockService

logger = logging.getLogger(__name__)


class CoverageManager(BaseStockService):
    """Coverage 메타데이터 관리 클래스

    Methods:
        - get_or_create_coverage: Coverage 조회 또는 생성
        - update_coverage: Coverage 업데이트
    """

    async def refresh_data_from_source(self, **kwargs) -> List[DailyPrice]:
        """베이스 클래스 추상 메서드 구현 (deprecated)"""
        logger.warning("refresh_data_from_source is deprecated in CoverageManager")
        return []

    async def get_or_create_coverage(
        self, symbol: str, data_type: str
    ) -> StockDataCoverage:
        """Coverage 레코드 조회 또는 생성

        Args:
            symbol: 종목 심볼
            data_type: 데이터 타입 (daily, weekly, monthly)

        Returns:
            StockDataCoverage 인스턴스
        """
        coverage = await StockDataCoverage.find_one(
            {"symbol": symbol, "data_type": data_type}
        )

        if not coverage:
            coverage = StockDataCoverage(
                symbol=symbol,
                data_type=data_type,
                is_active=True,
                update_frequency="daily",
                total_records=0,
                source="alpha_vantage",
                data_quality_score=0.0,
            )
            await coverage.insert()
            logger.info(f"Created new coverage for {symbol} ({data_type})")
        else:
            logger.debug(f"Found existing coverage for {symbol} ({data_type})")

        return coverage

    async def update_coverage(
        self,
        coverage: StockDataCoverage,
        data_records: Sequence[DailyPrice | WeeklyPrice | MonthlyPrice],
        update_type: Literal["full", "delta"],
    ) -> None:
        """Coverage 레코드 업데이트

        Args:
            coverage: 업데이트할 StockDataCoverage 인스턴스
            data_records: 데이터 레코드 리스트
            update_type: 'full' (전체 업데이트) 또는 'delta' (증분 업데이트)
        """
        if not data_records:
            logger.warning(
                f"No data records provided for coverage update: {coverage.symbol} ({coverage.data_type})"
            )
            return

        # 날짜 범위 계산
        dates = [record.date for record in data_records]
        first_date = min(dates)
        last_date = max(dates)

        # Coverage 메타데이터 업데이트
        coverage.total_records = len(data_records)
        coverage.first_date = first_date
        coverage.last_date = last_date

        # 업데이트 타임스탬프 설정
        now = datetime.now(timezone.utc)
        if update_type == "full":
            coverage.last_full_update = now
            logger.info(
                f"Full update completed for {coverage.symbol} ({coverage.data_type}): "
                f"{len(data_records)} records, {first_date.date()} ~ {last_date.date()}"
            )
        else:
            coverage.last_delta_update = now
            logger.info(
                f"Delta update completed for {coverage.symbol} ({coverage.data_type}): "
                f"{len(data_records)} records, {first_date.date()} ~ {last_date.date()}"
            )

        # 다음 업데이트 예정일 계산
        update_intervals = {"daily": 1, "weekly": 7, "monthly": 30}
        days_offset = update_intervals.get(coverage.data_type, 1)
        coverage.next_update_due = now + timedelta(days=days_offset)

        # MongoDB에 저장
        await coverage.save()
        logger.debug(
            f"Coverage saved: next update due at {coverage.next_update_due.isoformat()}"
        )
