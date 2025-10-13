"""DuckDB 데이터베이스 스키마 및 관리

주식 시계열 데이터와 메타데이터를 저장하기 위한 DuckDB 스키마
"""

from typing import Any
import logging
from pathlib import Path
from datetime import UTC, datetime

import duckdb
import pandas as pd

from app.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """DuckDB 데이터베이스 관리 클래스"""

    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or settings.DUCKDB_PATH
        self.connection: duckdb.DuckDBPyConnection | None = None

        # 데이터베이스 디렉토리 생성
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    @property
    def duckdb_conn(self) -> duckdb.DuckDBPyConnection:
        """DuckDB 연결 객체 반환 (alias for compatibility)"""
        if self.connection is None:
            self.connect()
        if self.connection is None:
            raise RuntimeError("DuckDB connection not established")
        return self.connection

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.close()

    def connect(self) -> None:
        """데이터베이스 연결"""
        if self.connection is None:
            logger.info(f"Connecting to DuckDB at: {self.db_path}")
            try:
                # 기존 연결이 있다면 종료
                self.close()
                # 새 연결 생성
                self.connection = duckdb.connect(self.db_path)
                self._create_tables()
                logger.info(f"✅ DuckDB connected successfully at: {self.db_path}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to DuckDB: {e}")
                # 파일이 잠겨있다면 메모리 DB로 폴백
                if "lock" in str(e).lower():
                    logger.warning("🔄 Falling back to in-memory database")
                    self.connection = duckdb.connect(":memory:")
                    self._create_tables()
                    logger.info("✅ DuckDB connected to in-memory database")
                else:
                    raise

    def close(self) -> None:
        """데이터베이스 연결 종료"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("🔒 DuckDB connection closed")
            except Exception as e:
                logger.warning(f"⚠️ Error closing DuckDB connection: {e}")
            finally:
                self.connection = None

    def _create_tables(self) -> None:
        """테이블 생성"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        # 주식 마스터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS stocks (
                symbol VARCHAR PRIMARY KEY,
                name VARCHAR,
                sector VARCHAR,
                industry VARCHAR,
                market_cap BIGINT,
                country VARCHAR,
                currency VARCHAR,
                exchange VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 일일 주가 데이터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_prices (
                symbol VARCHAR,
                date DATE,
                open DECIMAL(12, 4),
                high DECIMAL(12, 4),
                low DECIMAL(12, 4),
                close DECIMAL(12, 4),
                adjusted_close DECIMAL(12, 4),
                volume BIGINT,
                dividend_amount DECIMAL(8, 4) DEFAULT 0,
                split_coefficient DECIMAL(8, 4) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        """
        )

        # 주간 주가 데이터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS weekly_prices (
                symbol VARCHAR,
                date DATE,
                open DECIMAL(12, 4),
                high DECIMAL(12, 4),
                low DECIMAL(12, 4),
                close DECIMAL(12, 4),
                adjusted_close DECIMAL(12, 4),
                volume BIGINT,
                dividend_amount DECIMAL(8, 4) DEFAULT 0,
                split_coefficient DECIMAL(8, 4) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        """
        )

        # 월간 주가 데이터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS monthly_prices (
                symbol VARCHAR,
                date DATE,
                open DECIMAL(12, 4),
                high DECIMAL(12, 4),
                low DECIMAL(12, 4),
                close DECIMAL(12, 4),
                adjusted_close DECIMAL(12, 4),
                volume BIGINT,
                dividend_amount DECIMAL(8, 4) DEFAULT 0,
                split_coefficient DECIMAL(8, 4) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, date)
            )
        """
        )

        # 인트라데이 데이터 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS intraday_prices (
                symbol VARCHAR,
                datetime TIMESTAMP,
                interval_type VARCHAR,  -- '1min', '5min', '15min', '30min', '60min'
                open DECIMAL(12, 4),
                high DECIMAL(12, 4),
                low DECIMAL(12, 4),
                close DECIMAL(12, 4),
                volume BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (symbol, datetime, interval_type)
            )
        """
        )

        # 백테스트 결과 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS backtest_results (
                id VARCHAR PRIMARY KEY,
                strategy_name VARCHAR,
                symbols VARCHAR[],  -- 배열로 여러 심볼 지원
                start_date DATE,
                end_date DATE,
                initial_cash DECIMAL(15, 2),
                final_value DECIMAL(15, 2),
                total_return DECIMAL(8, 4),
                annual_return DECIMAL(8, 4),
                volatility DECIMAL(8, 4),
                sharpe_ratio DECIMAL(8, 4),
                max_drawdown DECIMAL(8, 4),
                parameters JSON,  -- 전략 파라미터
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 백테스트 포트폴리오 히스토리 테이블 (P3.2)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS backtest_portfolio_history (
                backtest_id VARCHAR,
                timestamp TIMESTAMP,
                total_value DECIMAL(15, 2),
                cash DECIMAL(15, 2),
                positions_value DECIMAL(15, 2),
                return_pct DECIMAL(8, 4),
                PRIMARY KEY (backtest_id, timestamp),
                FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
            )
        """
        )

        # 백테스트 거래 내역 테이블 (P3.2)
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS backtest_trades (
                backtest_id VARCHAR,
                trade_id VARCHAR,
                timestamp TIMESTAMP,
                symbol VARCHAR,
                side VARCHAR,  -- 'BUY' or 'SELL'
                quantity DECIMAL(12, 4),
                price DECIMAL(12, 4),
                commission DECIMAL(12, 4),
                total_amount DECIMAL(15, 2),
                PRIMARY KEY (backtest_id, trade_id),
                FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
            )
        """
        )

        # 거래 기록 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id VARCHAR PRIMARY KEY,
                backtest_id VARCHAR,
                symbol VARCHAR,
                datetime TIMESTAMP,
                action VARCHAR,  -- 'BUY', 'SELL'
                quantity INTEGER,
                price DECIMAL(12, 4),
                commission DECIMAL(8, 4) DEFAULT 0,
                value DECIMAL(15, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (backtest_id) REFERENCES backtest_results(id)
            )
        """
        )

        # 포트폴리오 확률 예측 기록 테이블
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio_forecast_history (
                as_of TIMESTAMP,
                horizon_days INTEGER,
                p05 DECIMAL(18, 4),
                p50 DECIMAL(18, 4),
                p95 DECIMAL(18, 4),
                expected_return_pct DECIMAL(9, 4),
                expected_volatility_pct DECIMAL(9, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # 통합 캐시 테이블 생성
        self._create_unified_cache_table()

        # 기술적 지표 캐시 테이블 생성
        self._create_technical_indicators_cache_table()

        # 인덱스 생성 (모든 테이블 생성 후)
        self._create_indexes()

        logger.info("데이터베이스 테이블 생성 완료")

    def _create_indexes(self) -> None:
        """인덱스 생성"""
        self._ensure_connected()
        if not self.connection:
            return

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol ON daily_prices(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_daily_prices_date ON daily_prices(date)",
            "CREATE INDEX IF NOT EXISTS idx_intraday_prices_symbol ON intraday_prices(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_intraday_prices_datetime ON intraday_prices(datetime)",
            "CREATE INDEX IF NOT EXISTS idx_trades_backtest_id ON trades(backtest_id)",
            "CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_trades_datetime ON trades(datetime)",
            # 통합 캐시 테이블 인덱스
            "CREATE INDEX IF NOT EXISTS idx_unified_cache_key ON unified_cache(cache_key)",
            "CREATE INDEX IF NOT EXISTS idx_unified_cache_data_type ON unified_cache(data_type)",
            "CREATE INDEX IF NOT EXISTS idx_unified_cache_symbol ON unified_cache(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_unified_cache_updated_at ON unified_cache(updated_at)",
            # 기술적 지표 캐시 테이블 인덱스
            "CREATE INDEX IF NOT EXISTS idx_ti_cache_key ON technical_indicators_cache(cache_key)",
            "CREATE INDEX IF NOT EXISTS idx_ti_symbol ON technical_indicators_cache(symbol)",
            "CREATE INDEX IF NOT EXISTS idx_ti_indicator_type ON technical_indicators_cache(indicator_type)",
            "CREATE INDEX IF NOT EXISTS idx_ti_cached_at ON technical_indicators_cache(cached_at)",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_forecast_as_of ON portfolio_forecast_history(as_of)",
            "CREATE INDEX IF NOT EXISTS idx_portfolio_forecast_horizon ON portfolio_forecast_history(horizon_days)",
        ]

        for index_sql in indexes:
            self.connection.execute(index_sql)

    def _ensure_connected(self) -> None:
        """연결이 없으면 자동으로 연결"""
        if self.connection is None:
            self.connect()

    def insert_stock_info(self, symbol: str, info: dict) -> None:
        """주식 정보 삽입/업데이트"""
        self._ensure_connected()

        if not self.connection:
            raise RuntimeError("데이터베이스 연결 실패")

        self.connection.execute(
            """
            INSERT OR REPLACE INTO stocks
            (symbol, name, sector, industry, market_cap, country, currency, exchange, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            [
                symbol,
                info.get("Name", ""),
                info.get("Sector", ""),
                info.get("Industry", ""),
                (
                    int(info.get("MarketCapitalization", 0))
                    if info.get("MarketCapitalization")
                    else None
                ),
                info.get("Country", ""),
                info.get("Currency", ""),
                info.get("Exchange", ""),
            ],
        )
        logger.info(f"주식 정보 저장됨: {symbol}")

    def insert_daily_prices(self, df: pd.DataFrame) -> int:
        """일일 주가 데이터 삽입"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        if df.empty:
            return 0

        # 필요한 컬럼만 선택하고 정렬
        required_columns = [
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "dividend_amount",
            "split_coefficient",
        ]

        # 인덱스를 date 컬럼으로 변환
        df_copy = df.copy()
        df_copy["date"] = df_copy.index.to_series().dt.date

        # 필요한 컬럼만 선택
        df_insert = df_copy[["date"] + required_columns].copy()

        # ON CONFLICT DO UPDATE 대신 INSERT OR REPLACE 사용
        rows_inserted = 0
        for _, row in df_insert.iterrows():
            self.connection.execute(
                """
                INSERT OR REPLACE INTO daily_prices
                (symbol, date, open, high, low, close, adjusted_close, volume,
                 dividend_amount, split_coefficient)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    row["symbol"],
                    row["date"],
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                    row["adjusted_close"],
                    row["volume"],
                    row["dividend_amount"],
                    row["split_coefficient"],
                ],
            )
            rows_inserted += 1

        logger.info(f"일일 주가 데이터 {rows_inserted}건 저장됨")
        return rows_inserted

    def insert_intraday_prices(self, df: pd.DataFrame, interval_type: str) -> int:
        """인트라데이 주가 데이터 삽입"""
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        if df.empty:
            return 0

        # 필요한 컬럼만 선택
        required_columns = ["symbol", "open", "high", "low", "close", "volume"]

        # 인덱스를 datetime 컬럼으로 변환
        df_copy = df.copy()
        df_copy["datetime"] = df_copy.index
        df_copy["interval_type"] = interval_type

        # 필요한 컬럼만 선택
        df_insert = df_copy[["datetime", "interval_type"] + required_columns].copy()

        rows_inserted = 0
        for _, row in df_insert.iterrows():
            self.connection.execute(
                """
                INSERT OR REPLACE INTO intraday_prices
                (symbol, datetime, interval_type, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                [
                    row["symbol"],
                    row["datetime"],
                    row["interval_type"],
                    row["open"],
                    row["high"],
                    row["low"],
                    row["close"],
                    row["volume"],
                ],
            )
            rows_inserted += 1

        logger.info(f"인트라데이 주가 데이터 {rows_inserted}건 저장됨")
        return rows_inserted

    def record_portfolio_forecast(
        self,
        *,
        as_of: datetime,
        horizon_days: int,
        p05: float,
        p50: float,
        p95: float,
        expected_return_pct: float,
        expected_volatility_pct: float,
    ) -> None:
        """Persist probabilistic KPI forecasts for analytics."""

        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        self.connection.execute(
            """
            INSERT INTO portfolio_forecast_history (
                as_of,
                horizon_days,
                p05,
                p50,
                p95,
                expected_return_pct,
                expected_volatility_pct,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
            [
                as_of,
                horizon_days,
                p05,
                p50,
                p95,
                expected_return_pct,
                expected_volatility_pct,
            ],
        )

    def get_daily_prices(
        self,
        symbol: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pd.DataFrame:
        """일일 주가 데이터 조회"""
        self._ensure_connected()
        if not self.connection:
            logger.warning("데이터베이스 연결 실패 - 빈 DataFrame 반환")
            return pd.DataFrame()

        try:
            base_query = "SELECT * FROM daily_prices WHERE symbol = ?"
            params = [symbol]

            if start_date:
                base_query += " AND date >= ?"
                params.append(start_date)

            if end_date:
                base_query += " AND date <= ?"
                params.append(end_date)

            base_query += " ORDER BY date"

            df = self.connection.execute(base_query, params).df()

            if not df.empty:
                # date 컬럼을 인덱스로 설정
                df["date"] = pd.to_datetime(df["date"])
                df.set_index("date", inplace=True)

            return df

        except Exception as e:
            logger.error(f"일일 주가 데이터 조회 중 오류: {e}")
            return pd.DataFrame()

    def get_available_symbols(self) -> list[str]:
        """사용 가능한 심볼 목록 조회"""
        self._ensure_connected()
        if not self.connection:
            logger.warning("데이터베이스 연결 실패 - 빈 목록 반환")
            return []

        try:
            result = self.connection.execute(
                "SELECT DISTINCT symbol FROM daily_prices ORDER BY symbol"
            ).fetchall()

            return [row[0] for row in result] if result else []

        except Exception as e:
            logger.error(f"심볼 목록 조회 중 오류: {e}")
            return []

    def get_data_range(self, symbol: str) -> tuple[str | None, str | None]:
        """심볼의 데이터 범위 조회"""
        self._ensure_connected()
        if not self.connection:
            logger.warning("데이터베이스 연결 실패 - None 반환")
            return None, None

        try:
            result = self.connection.execute(
                "SELECT MIN(date) as min_date, MAX(date) as max_date FROM daily_prices WHERE symbol = ?",
                [symbol],
            ).fetchone()

            if result and result[0] and result[1]:
                return str(result[0]), str(result[1])
            else:
                return None, None

        except Exception as e:
            logger.error(f"데이터 범위 조회 중 오류 (symbol: {symbol}): {e}")
            return None, None

    def save_backtest_result(self, result_data: dict) -> str:
        """백테스트 결과 저장"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        import json
        import uuid

        result_id = str(uuid.uuid4())

        self.connection.execute(
            """
            INSERT INTO backtest_results
            (id, strategy_name, symbols, start_date, end_date, initial_cash,
             final_value, total_return, annual_return, volatility, sharpe_ratio,
             max_drawdown, parameters)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            [
                result_id,
                result_data["strategy_name"],
                result_data["symbols"],
                result_data["start_date"],
                result_data["end_date"],
                result_data["initial_cash"],
                result_data["final_value"],
                result_data["total_return"],
                result_data["annual_return"],
                result_data["volatility"],
                result_data["sharpe_ratio"],
                result_data["max_drawdown"],
                json.dumps(result_data.get("parameters", {})),
            ],
        )

        logger.info(f"백테스트 결과 저장됨: {result_id}")
        return result_id

    def save_portfolio_history(
        self, backtest_id: str, portfolio_history: list[dict]
    ) -> int:
        """백테스트 포트폴리오 히스토리 저장 (P3.2)"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        if not portfolio_history:
            logger.warning(f"No portfolio history to save for {backtest_id}")
            return 0

        try:
            # DataFrame으로 변환하여 배치 삽입
            df = pd.DataFrame(portfolio_history)
            df["backtest_id"] = backtest_id

            self.connection.execute(
                """
                INSERT INTO backtest_portfolio_history
                (backtest_id, timestamp, total_value, cash, positions_value, return_pct)
                SELECT backtest_id, timestamp, total_value, cash, positions_value, return_pct
                FROM df
            """
            )

            count = len(portfolio_history)
            logger.info(f"포트폴리오 히스토리 {count}건 저장됨: {backtest_id}")
            return count

        except Exception as e:
            logger.error(f"포트폴리오 히스토리 저장 실패: {e}")
            return 0

    def save_trades_history(self, backtest_id: str, trades: list[dict]) -> int:
        """백테스트 거래 내역 저장 (P3.2)"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        if not trades:
            logger.warning(f"No trades to save for {backtest_id}")
            return 0

        try:
            import uuid

            # 거래 내역에 ID 추가
            trades_with_id = []
            for trade in trades:
                trade_copy = trade.copy()
                trade_copy["backtest_id"] = backtest_id
                trade_copy["trade_id"] = str(uuid.uuid4())
                trades_with_id.append(trade_copy)

            # DataFrame으로 변환하여 배치 삽입
            # DuckDB는 Python DataFrame을 SQL에서 직접 참조 가능
            trades_df = pd.DataFrame(trades_with_id)  # type: ignore # noqa: F841

            self.connection.execute(
                """
                INSERT INTO backtest_trades
                (backtest_id, trade_id, timestamp, symbol, side, quantity,
                 price, commission, total_amount)
                SELECT backtest_id, trade_id, timestamp, symbol, side, quantity,
                       price, commission, total_amount
                FROM trades_df
            """
            )

            count = len(trades)
            logger.info(f"거래 내역 {count}건 저장됨: {backtest_id}")
            return count

        except Exception as e:
            logger.error(f"거래 내역 저장 실패: {e}")
            return 0

    def get_portfolio_history(self, backtest_id: str) -> pd.DataFrame | None:
        """백테스트 포트폴리오 히스토리 조회 (P3.2)"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            df = self.connection.execute(
                """
                SELECT timestamp, total_value, cash, positions_value, return_pct
                FROM backtest_portfolio_history
                WHERE backtest_id = ?
                ORDER BY timestamp
            """,
                [backtest_id],
            ).df()

            if df.empty:
                logger.warning(f"No portfolio history found for {backtest_id}")
                return None

            return df

        except Exception as e:
            logger.error(f"포트폴리오 히스토리 조회 실패: {e}")
            return None

    def get_trades_history(self, backtest_id: str) -> pd.DataFrame | None:
        """백테스트 거래 내역 조회 (P3.2)"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            df = self.connection.execute(
                """
                SELECT trade_id, timestamp, symbol, side, quantity,
                       price, commission, total_amount
                FROM backtest_trades
                WHERE backtest_id = ?
                ORDER BY timestamp
            """,
                [backtest_id],
            ).df()

            if df.empty:
                logger.warning(f"No trades found for {backtest_id}")
                return None

            return df

        except Exception as e:
            logger.error(f"거래 내역 조회 실패: {e}")
            return None

    # ===== 캐시 관련 메서드들 =====

    def store_cache_data(
        self, cache_key: str, data: list[dict], table_name: str = "cache_data"
    ) -> bool:
        """DuckDB 캐시에 데이터 저장"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            # 캐시 테이블이 없으면 생성
            self._create_cache_table(table_name)

            # 기존 캐시 데이터 삭제
            self.connection.execute(
                f"DELETE FROM {table_name} WHERE cache_key = ?", [cache_key]
            )

            # 새 데이터 삽입
            if data:
                import json
                import uuid
                from datetime import datetime

                for item in data:
                    self.connection.execute(
                        f"""
                        INSERT INTO {table_name}
                        (id, cache_key, data_json, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """,
                        [
                            str(uuid.uuid4()),
                            cache_key,
                            json.dumps(item),
                            datetime.now(UTC),
                            datetime.now(UTC),
                        ],
                    )

                logger.info(f"DuckDB 캐시 저장 완료: {cache_key} ({len(data)} 항목)")
                return True
            return True

        except Exception as e:
            logger.error(f"DuckDB 캐시 저장 실패: {e}")
            return False

    def get_cache_data(
        self, cache_key: str, table_name: str = "cache_data", ttl_hours: int = 24
    ) -> list[dict] | None:
        """DuckDB 캐시에서 데이터 조회"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            from datetime import datetime, timedelta

            # TTL 체크
            ttl_threshold = datetime.now(UTC) - timedelta(hours=ttl_hours)

            results = self.connection.execute(
                f"""
                SELECT data_json FROM {table_name}
                WHERE cache_key = ? AND updated_at > ?
                ORDER BY created_at
            """,
                [cache_key, ttl_threshold],
            ).fetchall()

            if results:
                import json

                data = [json.loads(row[0]) for row in results]
                logger.info(f"DuckDB 캐시 조회 성공: {cache_key} ({len(data)} 항목)")
                return data
            else:
                logger.debug(f"DuckDB 캐시 미스: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"DuckDB 캐시 조회 실패: {e}")
            return None

    def clear_cache(
        self, cache_key: str | None = None, table_name: str = "cache_data"
    ) -> bool:
        """DuckDB 캐시 삭제"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            if cache_key:
                self.connection.execute(
                    f"DELETE FROM {table_name} WHERE cache_key = ?", [cache_key]
                )
                logger.info(f"DuckDB 캐시 삭제: {cache_key}")
            else:
                self.connection.execute(f"DELETE FROM {table_name}")
                logger.info(f"DuckDB 캐시 전체 삭제: {table_name}")
            return True

        except Exception as e:
            logger.error(f"DuckDB 캐시 삭제 실패: {e}")
            return False

    def _create_cache_table(self, table_name: str) -> None:
        """캐시 테이블 생성"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        # CREATE TABLE IF NOT EXISTS를 사용하여 기존 데이터 보존
        self.connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id VARCHAR PRIMARY KEY,
                cache_key VARCHAR NOT NULL,
                data_json TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            )
        """
        )

        # 인덱스 생성
        self.connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{table_name}_cache_key
            ON {table_name}(cache_key)
        """
        )

        self.connection.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{table_name}_updated_at
            ON {table_name}(updated_at)
        """
        )

    def _create_unified_cache_table(self) -> None:
        """통합 캐시 테이블 생성 - 모든 마켓 데이터 타입을 지원"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS unified_cache (
                id VARCHAR PRIMARY KEY,
                cache_key VARCHAR NOT NULL,
                data_type VARCHAR NOT NULL,  -- 'stock', 'fundamental', 'news', 'economic_indicator' 등
                symbol VARCHAR,              -- 심볼 (있는 경우)
                data_json TEXT NOT NULL,     -- JSON 직렬화된 데이터
                metadata JSON,               -- 추가 메타데이터 (검색 조건, 필터 등)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,        -- TTL 관리

                -- 복합 유니크 키로 중복 방지
                UNIQUE(cache_key, data_type, symbol)
            )
        """
        )

        # 기존 cache 테이블들도 유지 (하위 호환성)
        self._create_cache_table("market_data_cache")

        logger.info("통합 캐시 테이블 생성 완료")

    def _create_technical_indicators_cache_table(self) -> None:
        """기술적 지표 캐시 테이블 생성"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS technical_indicators_cache (
                cache_key VARCHAR NOT NULL,
                symbol VARCHAR NOT NULL,
                indicator_type VARCHAR NOT NULL,  -- 'SMA', 'EMA', 'RSI', 'MACD', etc.
                interval VARCHAR NOT NULL,        -- '1min', '5min', 'daily', etc.
                parameters_json TEXT,             -- JSON 직렬화된 파라미터
                date DATE,                        -- 날짜 (daily 이상)
                timestamp TIMESTAMP,              -- 타임스탬프 (intraday)
                value DECIMAL(18, 8),             -- 단일 값 (SMA, EMA, RSI 등)
                values_json TEXT,                 -- 복수 값 JSON (MACD, BBANDS 등)
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        logger.info("기술적 지표 캐시 테이블 생성 완료")

    # ===== 통합 캐시 관리 메서드들 =====

    def store_unified_cache(
        self,
        cache_key: str,
        data: list[dict] | dict,
        data_type: str,
        symbol: str | None = None,
        ttl_hours: int = 24,
        metadata: dict | None = None,
    ) -> bool:
        """통합 캐시에 데이터 저장

        Args:
            cache_key: 캐시 키
            data: 저장할 데이터 (단일 dict 또는 list[dict])
            data_type: 데이터 타입 ('stock', 'fundamental', 'news', 'economic_indicator' 등)
            symbol: 심볼 (옵션)
            ttl_hours: TTL (시간 단위)
            metadata: 추가 메타데이터
        """
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            import json
            import uuid
            from datetime import datetime, timedelta

            # 단일 데이터를 리스트로 변환
            if isinstance(data, dict):
                data = [data]

            # 디버깅: 데이터 타입 확인
            logger.info(
                f"📦 store_unified_cache 데이터 타입: {type(data)}, 길이: {len(data) if isinstance(data, list) else 'N/A'}"
            )
            if isinstance(data, list) and len(data) > 0:
                logger.info(f"📦 첫 번째 항목 타입: {type(data[0])}")

            # 기존 캐시 삭제
            self.connection.execute(
                """
                DELETE FROM unified_cache
                WHERE cache_key = ? AND data_type = ? AND (symbol = ? OR symbol IS NULL)
                """,
                [cache_key, data_type, symbol],
            )

            # 새 데이터 삽입
            expires_at = datetime.now(UTC) + timedelta(hours=ttl_hours)

            # ✅ 전체 배열을 하나의 JSON으로 직렬화
            serializable_data = [self._make_json_serializable(item) for item in data]

            self.connection.execute(
                """
                INSERT INTO unified_cache
                (id, cache_key, data_type, symbol, data_json, metadata, expires_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    str(uuid.uuid4()),
                    cache_key,
                    data_type,
                    symbol,
                    json.dumps(serializable_data),  # 전체 배열을 한 번에 저장
                    json.dumps(metadata) if metadata else None,
                    expires_at,
                ],
            )

            logger.info(f"통합 캐시 저장: {data_type}.{cache_key} ({len(data)} 항목)")
            return True

        except Exception as e:
            logger.error(f"통합 캐시 저장 실패: {e}")
            return False

    def get_unified_cache(
        self,
        cache_key: str,
        data_type: str,
        symbol: str | None = None,
        ignore_ttl: bool = False,
    ) -> list[dict] | None:
        """통합 캐시에서 데이터 조회"""
        self._ensure_connected()
        if not self.connection:
            raise RuntimeError("데이터베이스에 연결되지 않음")

        try:
            import json
            from datetime import datetime

            # TTL 체크 조건
            ttl_condition = (
                "" if ignore_ttl else "AND (expires_at IS NULL OR expires_at > ?)"
            )
            params = [cache_key, data_type, symbol]
            if not ignore_ttl:
                params.append(datetime.now(UTC))

            query = f"""
                SELECT data_json FROM unified_cache
                WHERE cache_key = ? AND data_type = ? AND (symbol = ? OR symbol IS NULL)
                {ttl_condition}
                ORDER BY created_at
            """

            results = self.connection.execute(query, params).fetchall()

            if results:
                # ✅ 첫 번째 행의 JSON을 파싱 (배열로 저장되어 있음)
                data = json.loads(results[0][0])
                logger.info(f"통합 캐시 HIT: {data_type}.{cache_key} ({len(data)} 항목)")
                return data
            else:
                logger.debug(f"통합 캐시 MISS: {data_type}.{cache_key}")
                return None

        except Exception as e:
            logger.error(f"통합 캐시 조회 실패: {e}")
            return None

    def _make_json_serializable(self, obj) -> Any:
        """객체를 JSON 직렬화 가능하도록 변환"""
        import json
        from datetime import datetime
        from decimal import Decimal

        if isinstance(obj, dict):
            return {
                key: self._make_json_serializable(value) for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif hasattr(obj, "model_dump"):  # Pydantic 모델
            return self._make_json_serializable(obj.model_dump())
        elif hasattr(obj, "dict"):  # Pydantic v1 스타일
            return self._make_json_serializable(obj.dict())
        else:
            # 기본 JSON 직렬화 시도
            try:
                json.dumps(obj)
                return obj
            except (TypeError, ValueError):
                return str(obj)


def get_database() -> DatabaseManager:
    """데이터베이스 매니저 인스턴스 생성"""
    return DatabaseManager()


if __name__ == "__main__":
    # 사용 예시
    with DatabaseManager() as db:
        # 테이블 생성 확인
        symbols = db.get_available_symbols()
        print(f"사용 가능한 심볼: {symbols}")

        # 데이터 기간 확인
        for symbol in symbols[:3]:  # 처음 3개만
            start, end = db.get_data_range(symbol)
            print(f"{symbol}: {start} ~ {end}")
