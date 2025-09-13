"""
통합 테스트 모듈

전체 시스템의 통합 테스트를 포함합니다.
- 서비스 간 통신 테스트
- 엔드투엔드 백테스트 워크플로우 테스트
- 성능 테스트
"""

from collections.abc import Generator

import pytest


@pytest.fixture(scope="session")
def test_database() -> Generator[str, None, None]:
    """테스트용 임시 데이터베이스 생성"""
    # TODO: 임시 DuckDB 데이터베이스 생성
    yield "test.db"
    # TODO: 정리 작업


@pytest.fixture
def sample_data():
    """테스트용 샘플 데이터"""
    # TODO: 테스트용 OHLCV 데이터 생성
    pass
