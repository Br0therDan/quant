#!/usr/bin/env python3
"""
통합 백엔드 실행 스크립트
"""

import subprocess
import sys
import os
from pathlib import Path


def main():
    """메인 실행 함수"""
    # 프로젝트 루트 디렉토리로 이동
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"

    if not backend_dir.exists():
        print("❌ Backend 디렉토리를 찾을 수 없습니다.")
        sys.exit(1)

    # backend 디렉토리로 이동하여 서버 실행
    os.chdir(backend_dir)

    try:
        print("🚀 통합 퀀트 백엔드 서버 시작...")
        print("📍 서버 주소: http://localhost:8000")
        print("📋 API 문서: http://localhost:8000/docs")
        print("⚡ 통합 테스트: http://localhost:8000/api/v1/integrated/test-services")
        print("=" * 60)

        # uvicorn으로 서버 실행
        subprocess.run(
            [
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            check=True,
        )

    except KeyboardInterrupt:
        print("\n🛑 서버가 중지되었습니다.")
    except subprocess.CalledProcessError as e:
        print(f"❌ 서버 실행 중 오류 발생: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
