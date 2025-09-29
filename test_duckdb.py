#!/usr/bin/env python3
"""DuckDB 연동 테스트"""

import sys
import os

sys.path.append("/Users/donghakim/quant")


def test_duckdb():
    try:
        from backend.app.services.database_manager import DatabaseManager

        print("🦆 DatabaseManager import 성공")

        # DatabaseManager 인스턴스 생성
        db = DatabaseManager()
        print(f"📁 DuckDB 파일 경로: {db.db_path}")

        # 연결 테스트
        db.connect()
        print(f"✅ DuckDB 연결 성공: {db.connection is not None}")

        # 테이블 존재 확인
        tables = db.connection.execute("SHOW TABLES").fetchall()
        print(f"📋 생성된 테이블 수: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")

        # 심볼 조회 테스트
        symbols = db.get_available_symbols()
        print(f"💰 사용 가능한 심볼 수: {len(symbols)}")
        if symbols:
            print(f"   샘플: {symbols[:5]}")

        # 연결 종료
        db.close()
        print("🔒 DuckDB 연결 종료")

        return True

    except Exception as e:
        print(f"❌ DuckDB 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_service_factory():
    try:
        from backend.app.services.service_factory import service_factory

        print("\n🏭 ServiceFactory 테스트")

        # DatabaseManager 생성 테스트
        db_manager = service_factory.get_database_manager()
        print(f"✅ DatabaseManager 생성: {db_manager is not None}")
        print(f"🔗 연결 상태: {db_manager.connection is not None}")

        return True

    except Exception as e:
        print(f"❌ ServiceFactory 테스트 실패: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 DuckDB 통합 테스트 시작\n")

    success1 = test_duckdb()
    success2 = test_service_factory()

    if success1 and success2:
        print("\n🎉 모든 테스트 성공!")
    else:
        print("\n💥 일부 테스트 실패!")
