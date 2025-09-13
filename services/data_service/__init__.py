"""데이터 서비스

Alpha Vantage API를 통한 주식 데이터 수집 및 DuckDB 저장
"""

from .alpha_vantage_client import AlphaVantageClient, get_stock_data
from .database import DatabaseManager, get_database
from .mock_data import MockDataGenerator, generate_mock_response
from .pipeline import DataPipeline, setup_default_symbols, update_watchlist

__all__ = [
    "AlphaVantageClient",
    "get_stock_data",
    "DatabaseManager",
    "get_database",
    "DataPipeline",
    "update_watchlist",
    "setup_default_symbols",
    "MockDataGenerator",
    "generate_mock_response",
]
