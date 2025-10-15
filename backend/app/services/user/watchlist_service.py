"""
Watchlist Service
사용자별 워치리스트 관리 서비스
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from app.models import Watchlist
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class WatchlistService:
    """워치리스트 관리 서비스

    사용자별 개인화된 워치리스트 생성, 수정, 조회 기능을 제공합니다.
    MarketDataService와 연동하여 워치리스트 심볼의 데이터를 자동 수집합니다.
    """

    def __init__(self):
        self.settings = get_settings()
        self.market_service = None  # Lazy loading으로 순환 참조 방지

    async def _get_market_service(self):
        """MarketDataService lazy loading"""
        if self.market_service is None:
            from app.services.service_factory import service_factory

            self.market_service = service_factory.get_market_data_service()
        return self.market_service

    async def create_watchlist(
        self,
        name: str,
        symbols: List[str],
        description: str = "",
        user_id: Optional[str] = None,
        auto_update: bool = True,
        update_interval: int = 3600,
    ) -> Optional[Watchlist]:
        """새로운 워치리스트 생성

        Args:
            name: 워치리스트 이름
            symbols: 심볼 리스트
            description: 설명 (선택사항)
            user_id: 사용자 ID (선택사항, None이면 공개 워치리스트)
            auto_update: 자동 업데이트 여부
            update_interval: 업데이트 간격 (초)

        Returns:
            생성된 Watchlist 객체 또는 None (실패 시)
        """
        try:
            # 중복 이름 체크
            existing = await self.get_watchlist(name, user_id)
            if existing:
                logger.warning(f"Watchlist '{name}' already exists for user {user_id}")
                return None

            # 심볼 정규화 (대문자 변환)
            normalized_symbols = [symbol.upper() for symbol in symbols]

            # 워치리스트 생성
            watchlist = Watchlist(
                name=name,
                description=description,
                symbols=normalized_symbols,
                user_id=user_id,
                auto_update=auto_update,
                update_interval=update_interval,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
                last_updated=None,
            )

            await watchlist.insert()
            logger.info(f"Created watchlist '{name}' with {len(symbols)} symbols")

            # 심볼 데이터 자동 수집 트리거 (백그라운드)
            if auto_update:
                await self._trigger_data_collection(normalized_symbols)

            return watchlist

        except Exception as e:
            logger.error(f"Failed to create watchlist '{name}': {e}")
            return None

    async def update_watchlist(
        self,
        name: str,
        user_id: Optional[str] = None,
        symbols: Optional[List[str]] = None,
        description: Optional[str] = None,
        auto_update: Optional[bool] = None,
        update_interval: Optional[int] = None,
    ) -> Optional[Watchlist]:
        """기존 워치리스트 업데이트

        Args:
            name: 워치리스트 이름
            user_id: 사용자 ID
            symbols: 새로운 심볼 리스트 (선택사항)
            description: 새로운 설명 (선택사항)
            auto_update: 자동 업데이트 설정 (선택사항)
            update_interval: 업데이트 간격 (선택사항)

        Returns:
            업데이트된 Watchlist 객체 또는 None (실패 시)
        """
        try:
            watchlist = await self.get_watchlist(name, user_id)
            if not watchlist:
                logger.warning(f"Watchlist '{name}' not found for user {user_id}")
                return None

            # 필드 업데이트
            if symbols is not None:
                watchlist.symbols = [symbol.upper() for symbol in symbols]
            if description is not None:
                watchlist.description = description
            if auto_update is not None:
                watchlist.auto_update = auto_update
            if update_interval is not None:
                watchlist.update_interval = update_interval

            watchlist.updated_at = datetime.now(timezone.utc)
            await watchlist.save()

            logger.info(f"Updated watchlist '{name}' for user {user_id}")

            # 새로운 심볼이 있으면 데이터 수집 트리거
            if symbols and watchlist.auto_update:
                await self._trigger_data_collection(watchlist.symbols)

            return watchlist

        except Exception as e:
            logger.error(f"Failed to update watchlist '{name}': {e}")
            return None

    async def get_watchlist(
        self, name: str, user_id: Optional[str] = None
    ) -> Optional[Watchlist]:
        """워치리스트 조회

        Args:
            name: 워치리스트 이름
            user_id: 사용자 ID (None이면 공개 워치리스트 조회)

        Returns:
            Watchlist 객체 또는 None (없을 시)
        """
        try:
            if user_id:
                return await Watchlist.find_one(
                    Watchlist.name == name, Watchlist.user_id == user_id
                )
            else:
                return await Watchlist.find_one(
                    Watchlist.name == name, Watchlist.user_id is None
                )
        except Exception as e:
            logger.error(f"Failed to get watchlist '{name}': {e}")
            return None

    async def list_watchlists(self, user_id: Optional[str] = None) -> List[Watchlist]:
        """사용자의 모든 워치리스트 조회

        Args:
            user_id: 사용자 ID (None이면 공개 워치리스트들)

        Returns:
            Watchlist 객체들의 리스트
        """
        try:
            if user_id:
                return await Watchlist.find(Watchlist.user_id == user_id).to_list()
            else:
                return await Watchlist.find(Watchlist.user_id is None).to_list()
        except Exception as e:
            logger.error(f"Failed to list watchlists for user {user_id}: {e}")
            return []

    async def delete_watchlist(self, name: str, user_id: Optional[str] = None) -> bool:
        """워치리스트 삭제

        Args:
            name: 워치리스트 이름
            user_id: 사용자 ID

        Returns:
            삭제 성공 여부
        """
        try:
            watchlist = await self.get_watchlist(name, user_id)
            if not watchlist:
                logger.warning(f"Watchlist '{name}' not found for deletion")
                return False

            await watchlist.delete()
            logger.info(f"Deleted watchlist '{name}' for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete watchlist '{name}': {e}")
            return False

    async def get_default_symbols(self) -> List[str]:
        """기본 심볼 리스트 반환

        Returns:
            기본 심볼 리스트
        """
        return [
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
            "META",
            "NVDA",
            "JPM",
            "JNJ",
            "V",
        ]

    async def setup_default_watchlist(
        self, user_id: Optional[str] = None
    ) -> Optional[Watchlist]:
        """기본 워치리스트 설정

        Args:
            user_id: 사용자 ID (None이면 공개 기본 워치리스트)

        Returns:
            생성된 기본 워치리스트
        """
        try:
            default_symbols = await self.get_default_symbols()

            return await self.create_watchlist(
                name="default",
                symbols=default_symbols,
                description="Default watchlist with popular stocks",
                user_id=user_id,
                auto_update=True,
            )
        except Exception as e:
            logger.error(f"Failed to setup default watchlist: {e}")
            return None

    async def _trigger_data_collection(self, symbols: List[str]) -> None:
        """워치리스트 심볼의 데이터 수집 트리거 (백그라운드)

        Args:
            symbols: 수집할 심볼 리스트
        """
        try:
            market_service = await self._get_market_service()

            # 비동기적으로 데이터 수집 (에러가 있어도 워치리스트 생성은 성공)
            for symbol in symbols:
                try:
                    # Company 정보 수집
                    await market_service.fundamental.get_company_overview(symbol)
                    # 최근 주가 데이터 수집
                    await market_service.stock.get_daily_prices(
                        symbol, outputsize="compact"
                    )
                except Exception as e:
                    logger.warning(f"Failed to collect data for {symbol}: {e}")

        except Exception as e:
            logger.warning(f"Data collection trigger failed: {e}")

    async def get_watchlist_coverage(
        self, name: str, user_id: Optional[str] = None
    ) -> dict:
        """워치리스트의 데이터 커버리지 정보 반환

        Args:
            name: 워치리스트 이름
            user_id: 사용자 ID

        Returns:
            커버리지 정보 딕셔너리
        """
        try:
            watchlist = await self.get_watchlist(name, user_id)
            if not watchlist:
                return {"error": "Watchlist not found"}

            market_service = await self._get_market_service()
            coverage_info = {
                "watchlist_name": name,
                "total_symbols": len(watchlist.symbols),
                "symbols_coverage": {},
                "last_update": watchlist.updated_at,
            }

            # 각 심볼의 데이터 커버리지 확인
            for symbol in watchlist.symbols:
                try:
                    # Company 정보 확인
                    company_data = (
                        await market_service.fundamental.get_company_overview(symbol)
                    )

                    # 주가 데이터 확인 (간단한 체크)
                    market_data = await market_service.stock.get_daily_prices(
                        symbol, outputsize="compact"
                    )

                    coverage_info["symbols_coverage"][symbol] = {
                        "company_info": bool(company_data),
                        "market_data": bool(market_data),
                        "status": (
                            "complete" if (company_data and market_data) else "partial"
                        ),
                    }
                except Exception as e:
                    coverage_info["symbols_coverage"][symbol] = {
                        "company_info": False,
                        "market_data": False,
                        "status": "error",
                        "error": str(e),
                    }

            return coverage_info

        except Exception as e:
            logger.error(f"Failed to get coverage for watchlist '{name}': {e}")
            return {"error": str(e)}
