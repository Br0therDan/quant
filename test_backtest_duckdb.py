#!/usr/bin/env python3
"""BacktestService DuckDB 통합 테스트"""

import sys
import os

sys.path.append("/Users/donghakim/quant")


def test_backtest_service_duckdb():
    try:
        from backend.app.services.service_factory import service_factory

        print("🧪 BacktestService DuckDB 통합 테스트")

        # BacktestService 인스턴스 생성
        backtest_service = service_factory.get_backtest_service()

        print(f"✅ BacktestService 생성: {backtest_service is not None}")
        print(f"🗄️ DatabaseManager 주입: {backtest_service.database_manager is not None}")

        if backtest_service.database_manager:
            db = backtest_service.database_manager
            print(f"🔗 DuckDB 연결 상태: {db.connection is not None}")

            # DuckDB 백테스트 결과 요약 테스트
            results = backtest_service.get_duckdb_results_summary()
            print(f"📊 저장된 백테스트 결과 수: {len(results)}")

            # 테스트 백테스트 결과 저장
            test_result_data = {
                "strategy_name": "Test Strategy",
                "symbols": ["AAPL", "MSFT"],
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "initial_cash": 100000.0,
                "final_value": 120000.0,
                "total_return": 0.2,
                "annual_return": 0.18,
                "volatility": 0.15,
                "sharpe_ratio": 1.2,
                "max_drawdown": 0.08,
                "parameters": {"test": True},
            }

            result_id = db.save_backtest_result(test_result_data)
            print(f"💾 테스트 결과 저장 ID: {result_id}")

            # 저장 후 조회 테스트
            updated_results = backtest_service.get_duckdb_results_summary()
            print(f"📈 업데이트된 결과 수: {len(updated_results)}")

            if updated_results:
                latest = updated_results[0]
                print(
                    f"   최신 결과: {latest['strategy_name']}, 수익률: {latest['total_return']}"
                )

        return True

    except Exception as e:
        print(f"❌ BacktestService DuckDB 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_backtest_service_duckdb()

    if success:
        print("\n🎉 BacktestService DuckDB 통합 테스트 성공!")
    else:
        print("\n💥 BacktestService DuckDB 통합 테스트 실패!")
