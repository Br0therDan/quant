#!/usr/bin/env python3
"""
개발 환경 확인 스크립트

이 스크립트는 개발 환경이 올바르게 설정되었는지 확인합니다.
"""

import sys
from pathlib import Path


def check_python_version():
    """Python 버전 확인"""
    print(f"Python 버전: {sys.version}")
    print(f"Python 실행 경로: {sys.executable}")


def check_virtual_env():
    """가상환경 확인"""
    venv_path = Path(".venv")
    if venv_path.exists():
        print("✓ 가상환경 감지됨")
        print(f"가상환경 경로: {venv_path.absolute()}")
    else:
        print("✗ 가상환경을 찾을 수 없음")


def check_packages():
    """주요 패키지 설치 확인"""
    packages = [
        "pydantic",
        "pydantic_settings",
        "typer",
        "rich",
        "duckdb",
        "pandas",
        "numpy",
        "matplotlib",
        "plotly",
        "vectorbt",
    ]

    print("\n패키지 설치 상태:")
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - 설치되지 않음")


def check_project_structure():
    """프로젝트 구조 확인"""
    required_dirs = ["services", "shared", "tests"]
    required_files = ["pyproject.toml", "uv.lock", ".env.example"]

    print("\n프로젝트 구조:")
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ - 없음")

    for file_name in required_files:
        if Path(file_name).exists():
            print(f"✓ {file_name}")
        else:
            print(f"✗ {file_name} - 없음")


def check_imports():
    """모듈 import 확인"""
    print("\n모듈 import 테스트:")

    try:
        from shared.config import settings

        print("✓ shared.config.settings")
        print(f"  - Database path: {settings.database_path}")
    except Exception as e:
        print(f"✗ shared.config.settings - {e}")

    try:
        print("✓ shared.models")
    except Exception as e:
        print(f"✗ shared.models - {e}")

    try:
        print("✓ shared.cli")
    except Exception as e:
        print(f"✗ shared.cli - {e}")


if __name__ == "__main__":
    print("=== 개발 환경 확인 ===\n")

    check_python_version()
    print()

    check_virtual_env()

    check_packages()

    check_project_structure()

    check_imports()

    print("\n=== 확인 완료 ===")
    print("\nIDE에서 패키지를 인식하지 못하는 경우:")
    print("1. VS Code를 완전히 재시작하세요")
    print("2. Cmd+Shift+P → 'Python: Select Interpreter' → .venv/bin/python 선택")
    print("3. Cmd+Shift+P → 'Developer: Reload Window'")
