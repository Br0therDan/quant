"""시장 데이터 검증기

심볼, 날짜 범위, 데이터 품질 검증 로직을 제공합니다.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketDataValidator:
    """시장 데이터 검증기

    심볼, 날짜 범위, 데이터 무결성 등을 검증합니다.
    """

    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """심볼 검증

        Args:
            symbol: 주식 심볼 (예: AAPL, GOOGL)

        Returns:
            정규화된 심볼 (대문자)

        Raises:
            ValueError: 심볼이 유효하지 않을 때

        Example:
            >>> symbol = MarketDataValidator.validate_symbol("aapl")
            >>> print(symbol)
            AAPL
        """
        if not symbol:
            raise ValueError("Symbol is required")

        if not isinstance(symbol, str):
            raise ValueError("Symbol must be a string")

        # 공백 제거
        symbol = symbol.strip()

        if not symbol:
            raise ValueError("Symbol cannot be empty or whitespace")

        # 길이 검증
        if len(symbol) > 10:
            raise ValueError("Symbol is too long (max 10 characters)")

        # 알파벳 + 숫자만 허용
        if not symbol.replace(".", "").replace("-", "").isalnum():
            raise ValueError(
                "Symbol must contain only alphanumeric characters, dots, and hyphens"
            )

        return symbol.upper()

    @staticmethod
    def validate_date_range(
        start_date: str | datetime,
        end_date: str | datetime,
    ) -> tuple[datetime, datetime]:
        """날짜 범위 검증

        Args:
            start_date: 시작일 (YYYY-MM-DD 또는 datetime)
            end_date: 종료일 (YYYY-MM-DD 또는 datetime)

        Returns:
            (시작일, 종료일) datetime 객체

        Raises:
            ValueError: 날짜 형식이 잘못되었거나 범위가 유효하지 않을 때
        """
        # 문자열을 datetime으로 변환
        if isinstance(start_date, str):
            try:
                start_dt = datetime.fromisoformat(start_date)
            except ValueError as e:
                raise ValueError(
                    f"Invalid start_date format. Expected YYYY-MM-DD, got {start_date}"
                ) from e
        else:
            start_dt = start_date

        if isinstance(end_date, str):
            try:
                end_dt = datetime.fromisoformat(end_date)
            except ValueError as e:
                raise ValueError(
                    f"Invalid end_date format. Expected YYYY-MM-DD, got {end_date}"
                ) from e
        else:
            end_dt = end_date

        # 날짜 범위 검증
        if start_dt > end_dt:
            raise ValueError(
                f"start_date ({start_dt.date()}) must be before end_date ({end_dt.date()})"
            )

        # 과거 데이터만 허용 (미래 데이터 방지)
        now = datetime.now()
        if end_dt > now:
            logger.warning(
                f"end_date ({end_dt.date()}) is in the future. Using today's date."
            )
            end_dt = now

        return start_dt, end_dt

    @staticmethod
    def validate_interval(interval: str) -> str:
        """데이터 간격 검증

        Args:
            interval: 데이터 간격 (예: 1d, 1h, 5m)

        Returns:
            정규화된 간격

        Raises:
            ValueError: 간격이 유효하지 않을 때
        """
        valid_intervals = ["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1mo"]

        if interval not in valid_intervals:
            raise ValueError(
                f"Invalid interval: {interval}. "
                f"Valid intervals: {', '.join(valid_intervals)}"
            )

        return interval

    @staticmethod
    def validate_data_completeness(
        data_points: list,
        expected_count: int | None = None,
        min_count: int = 10,
    ) -> bool:
        """데이터 완전성 검증

        Args:
            data_points: 데이터 포인트 리스트
            expected_count: 예상 데이터 개수 (선택)
            min_count: 최소 데이터 개수 (기본값 10)

        Returns:
            True if valid

        Raises:
            ValueError: 데이터가 불완전할 때
        """
        if not data_points:
            raise ValueError("No data points provided")

        if len(data_points) < min_count:
            raise ValueError(
                f"Insufficient data: {len(data_points)} points "
                f"(minimum required: {min_count})"
            )

        if expected_count is not None and len(data_points) < expected_count * 0.8:
            logger.warning(
                f"Data completeness low: {len(data_points)}/{expected_count} "
                f"({len(data_points)/expected_count*100:.1f}%)"
            )

        return True
