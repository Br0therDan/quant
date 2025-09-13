# UV 프로젝트 초기화 가이드

## 기존 Poetry 환경 정리
```bash
# Poetry 관련 파일 제거 (필요시)
rm -f poetry.lock
rm -rf .venv

# Poetry 가상환경 제거 (필요시)
poetry env remove python
```

## UV 환경 초기화
```bash
# UV 설치
curl -LsSf https://astral.sh/uv/install.sh | sh

# 프로젝트 초기화 (기존 pyproject.toml 사용)
uv sync --dev

# 가상환경 활성화
source .venv/bin/activate  # Linux/macOS
# 또는
.venv\Scripts\activate     # Windows

# 개발 도구 설정
uv run pre-commit install
```

## 주요 UV 명령어
```bash
# 패키지 추가
uv add requests>=2.31.0

# 개발 의존성 추가
uv add --dev pytest>=7.4.0

# 의존성 설치/업데이트
uv sync

# 스크립트 실행
uv run quant --help

# Python 버전 관리
uv python install 3.12
uv python pin 3.12
```

## 기존 Poetry 사용자를 위한 명령어 대응표
| Poetry | UV |
|--------|-----|
| `poetry install` | `uv sync` |
| `poetry add package` | `uv add package` |
| `poetry add --group dev package` | `uv add --dev package` |
| `poetry run command` | `uv run command` |
| `poetry shell` | `source .venv/bin/activate` |
| `poetry env info` | `uv python list` |
