#!/usr/bin/env python3
"""
Manual script to run stock data update tasks
주식 데이터 업데이트 작업 수동 실행 스크립트

사용법:
    # 만료된 데이터만 업데이트 (Delta update)
    python scripts/run_stock_update.py

    # 모든 활성 심볼 강제 Full update (주의: API 호출 많음)
    python scripts/run_stock_update.py --force-all
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import after path setup
from app.core.config import settings
from app.tasks.stock_update import (
    update_stock_data_coverage,
    force_update_all_active_symbols,
)
from mysingle_quant.core import init_mongodb_async


async def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="Stock data update task runner")
    parser.add_argument(
        "--force-all",
        action="store_true",
        help="Force full update for all active symbols (uses many API calls)",
    )

    args = parser.parse_args()

    # MongoDB 연결
    print("📡 Connecting to MongoDB...")

    # Import models after MongoDB connection
    from app import models

    await init_mongodb_async(
        service_name=settings.SERVICE_NAME,
        document_models=models.collections,
    )

    print("✅ MongoDB connected")

    # 작업 실행
    if args.force_all:
        print("\n⚠️  WARNING: This will force full update for all active symbols!")
        print("⚠️  This may consume a lot of Alpha Vantage API calls!")

        confirm = input("\nContinue? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Cancelled")
            return

        print("\n🔄 Running forced full update...")
        result = await force_update_all_active_symbols()
    else:
        print("\n🔄 Running delta update for expired coverages...")
        result = await update_stock_data_coverage()

    # 결과 출력
    print("\n" + "=" * 60)
    print("📊 Update Results:")
    print("=" * 60)

    if "total_symbols" in result:
        print(f"Total symbols: {result['total_symbols']}")
    elif "total" in result:
        print(f"Total coverages: {result['total']}")

    print(f"✅ Success: {result['success']}")
    print(f"❌ Failed: {result['failed']}")

    if result["errors"]:
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for error in result["errors"][:10]:  # 최대 10개만 출력
            print(f"  - {error}")

        if len(result["errors"]) > 10:
            print(f"  ... and {len(result['errors']) - 10} more errors")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
