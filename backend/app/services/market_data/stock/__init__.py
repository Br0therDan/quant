"""
Stock Service Package
주식 서비스 - Phase 2.1b-1 (Partial Implementation)

현재 구현:
- ✅ base.py: BaseStockService (공통 로직)
- ✅ fetcher.py: StockFetcher (Alpha Vantage API 호출)
- ⏸️ storage.py: MongoDB 저장 (다음 세션)
- ⏸️ coverage.py: Coverage 관리 (다음 세션)
- ⏸️ cache.py: DuckDB 캐싱 (다음 세션)

임시 방식: stock_legacy.py를 import하여 완전 호환성 유지
"""

# stock_legacy.py에서 기존 StockService import
from ..stock_legacy import StockService as LegacyStockService

# 새로 구현된 모듈들 export
from .base import BaseStockService  # noqa: F401
from .fetcher import StockFetcher  # noqa: F401


# Phase 2.1b-1: 임시로 legacy를 그대로 사용
# Phase 2.1b-2에서 완전한 modular 구조로 전환 예정
StockService = LegacyStockService


__all__ = ["StockService", "BaseStockService", "StockFetcher"]
