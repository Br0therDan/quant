"""DuckDB 데이터베이스 스키마 및 관리

주식 시계열 데이터와 메타데이터를 저장하기 위한 DuckDB 스키마
"""

import logging
from pathlib import Path

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
                else:
                    raise
            self.connection = duckdb.connect(self.db_path)
            self._create_tables()
            logger.info(f"데이터베이스 연결됨: {self.db_path}")

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

        # 인덱스 생성
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
                from datetime import datetime

                for item in data:
                    self.connection.execute(
                        f"""
                        INSERT INTO {table_name}
                        (cache_key, data_json, created_at, updated_at)
                        VALUES (?, ?, ?, ?)
                    """,
                        [
                            cache_key,
                            json.dumps(item),
                            datetime.utcnow(),
                            datetime.utcnow(),
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
            ttl_threshold = datetime.utcnow() - timedelta(hours=ttl_hours)

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

        self.connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY,
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
