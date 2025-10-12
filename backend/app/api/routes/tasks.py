"""
Task management API endpoints
작업 관리 API 엔드포인트
"""

import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.tasks.stock_update import (
    update_stock_data_coverage,
    force_update_all_active_symbols,
)


router = APIRouter()
logger = logging.getLogger(__name__)


class TaskResult(BaseModel):
    """작업 실행 결과"""

    status: str
    message: str
    total: int = 0
    success: int = 0
    failed: int = 0
    errors: list[str] = []


@router.post(
    "/stock-update/delta",
    response_model=TaskResult,
    description="만료된 주식 데이터를 증분 업데이트합니다.",
)
async def run_stock_delta_update(background_tasks: BackgroundTasks):
    """
    StockDataCoverage의 next_update_due를 기준으로 만료된 데이터만 업데이트

    - Daily: 최근 100개 데이터 (compact)
    - Weekly/Monthly: 전체 데이터 (full)
    """
    try:
        logger.info("📡 Triggering stock delta update task...")

        # 백그라운드 작업으로 실행
        result = await update_stock_data_coverage()

        return TaskResult(
            status="completed",
            message=f"Delta update completed: {result['success']} success, {result['failed']} failed",
            total=result["total"],
            success=result["success"],
            failed=result["failed"],
            errors=result["errors"][:10],  # 최대 10개 에러만 반환
        )

    except Exception as e:
        logger.error(f"❌ Stock delta update failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to run stock delta update: {str(e)}"
        )


@router.post(
    "/stock-update/force-all",
    response_model=TaskResult,
    description="모든 활성 심볼의 주식 데이터를 강제 전체 업데이트합니다.",
)
async def run_stock_force_update(background_tasks: BackgroundTasks):
    """
    모든 활성 심볼의 데이터를 Full update

    ⚠️ 주의: 많은 Alpha Vantage API 호출을 발생시킵니다!
    일일 API 한도(500 calls)를 고려하여 사용하세요.
    """
    try:
        logger.info("📡 Triggering forced full update task...")

        # 백그라운드 작업으로 실행
        result = await force_update_all_active_symbols()

        return TaskResult(
            status="completed",
            message=f"Forced full update completed: {result['success']} success, {result['failed']} failed",
            total=result.get("total_symbols", 0),
            success=result["success"],
            failed=result["failed"],
            errors=result["errors"][:10],  # 최대 10개 에러만 반환
        )

    except Exception as e:
        logger.error(f"❌ Forced full update failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to run forced full update: {str(e)}"
        )


@router.get(
    "/stock-update/status",
    description="주식 데이터 업데이트 상태를 조회합니다.",
)
async def get_stock_update_status():
    """
    현재 업데이트가 필요한 Coverage 수 조회
    """
    try:
        from datetime import datetime
        from app.models.market_data.stock import StockDataCoverage

        now = datetime.utcnow()

        # 만료된 Coverage 수
        expired_count = await StockDataCoverage.find(
            {"is_active": True, "next_update_due": {"$lte": now}}
        ).count()

        # 전체 활성 Coverage 수
        total_count = await StockDataCoverage.find({"is_active": True}).count()

        return {
            "status": "ok",
            "total_active_coverages": total_count,
            "expired_coverages": expired_count,
            "update_needed": expired_count > 0,
            "timestamp": now.isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Failed to get update status: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to get update status: {str(e)}"
        )
