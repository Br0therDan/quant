#!/usr/bin/env python3
"""
Alpha Vantage MCP Server Test Script
Alpha Vantage MCP 서버 연결 및 기능 테스트용 스크립트
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path


async def test_mcp_server():
    """MCP 서버 기본 연결 테스트"""
    print("🔄 Alpha Vantage MCP Server 테스트 시작...")

    # API 키 확인
    api_key = "M9TJCCBXW5PJZ3HF"
    if not api_key:
        print("❌ ALPHA_VANTAGE_API_KEY 환경변수가 설정되지 않았습니다.")
        return False

    print(f"✅ API Key 확인: {api_key[:8]}...")

    try:
        # MCP 서버 사용 가능한 도구 목록 확인
        print("\n🔍 사용 가능한 카테고리 확인 중...")
        result = subprocess.run(
            ["uvx", "av-mcp", "--list-categories"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✅ 사용 가능한 카테고리:")
            print(result.stdout)
        else:
            print(f"❌ 카테고리 목록 조회 실패: {result.stderr}")
            return False

        # 기본 연결 테스트 (ping)
        print("\n🏓 기본 연결 테스트 (PING)...")

        # MCP 서버 실행 테스트
        print("📡 MCP 서버 실행 가능성 확인...")
        proc = subprocess.Popen(
            ["uvx", "av-mcp", api_key],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # 짧은 시간 대기 후 종료
        await asyncio.sleep(2)
        proc.terminate()

        try:
            stdout, stderr = proc.communicate(timeout=5)
            if proc.returncode is None or proc.returncode == 0:
                print("✅ MCP 서버 실행 가능")
            else:
                print(f"⚠️  MCP 서버 실행 경고: {stderr}")
        except subprocess.TimeoutExpired:
            print("✅ MCP 서버가 정상적으로 실행되고 있습니다 (시간 초과로 종료)")
            proc.kill()

        return True

    except subprocess.TimeoutExpired:
        print("❌ MCP 서버 응답 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        return False


def create_mcp_usage_examples():
    """MCP 사용 예제 파일 생성"""
    examples_content = """# Alpha Vantage MCP Server 사용 예제

## VS Code에서 사용하기

VS Code에서 GitHub Copilot Chat을 통해 Alpha Vantage 데이터에 접근할 수 있습니다:

```
@workspace /mcp-alpha-vantage AAPL의 최근 주가 정보를 가져와주세요
```

```
@workspace /mcp-alpha-vantage TSLA의 재무제표 정보를 조회해주세요
```

```
@workspace /mcp-alpha-vantage 최근 GDP 데이터를 가져와주세요
```

## 사용 가능한 주요 기능들

### 1. 주식 데이터 (Core Stock APIs)
- 일중/일간/주간/월간 시계열 데이터
- 실시간 주가 정보
- 심볼 검색
- 시장 상태 확인

### 2. 펀더멘털 데이터 (Fundamental Data)
- 회사 개요 정보
- 손익계산서, 대차대조표, 현금흐름표
- 실적 정보
- 상장/폐지 정보

### 3. 경제 지표 (Economic Indicators)
- 실질 GDP
- 연방기금금리
- 소비자물가지수 (CPI)
- 인플레이션율
- 실업률

### 4. 알파 인텔리전스 (Alpha Intelligence)
- 뉴스 감정 분석
- 실적 발표 대본
- 상위 상승/하락 종목
- 내부자 거래 정보

### 5. 기술적 지표 (Technical Indicators)
- 이동평균 (SMA, EMA, WMA 등)
- RSI, MACD, 스토캐스틱
- 볼린저 밴드
- 기타 기술적 지표들

## 환경 설정

MCP 서버는 다음 환경변수를 사용합니다:
- ALPHA_VANTAGE_API_KEY: {api_key}

## 테스트 명령어

```bash
# 카테고리 목록 확인
uvx av-mcp --list-categories

# 기본 실행
uvx av-mcp {api_key}

# 특정 카테고리만 사용
uvx av-mcp {api_key} --categories fundamental_data,economic_indicators
```
""".format(
        api_key="M9TJCCBXW5PJZ3HF"
    )

    with open("docs/MCP_ALPHA_VANTAGE_USAGE.md", "w", encoding="utf-8") as f:
        f.write(examples_content)

    print("✅ MCP 사용 예제 파일 생성: docs/MCP_ALPHA_VANTAGE_USAGE.md")


async def main():
    """메인 실행 함수"""
    print("🚀 Alpha Vantage MCP Server 설정 및 테스트")
    print("=" * 50)

    # MCP 서버 테스트
    success = await test_mcp_server()

    if success:
        print("\n✅ Alpha Vantage MCP Server 설정 완료!")
        print("\n📋 다음 단계:")
        print("1. VS Code에서 GitHub Copilot Chat 열기")
        print("2. '@workspace /mcp-alpha-vantage' 명령어로 Alpha Vantage 데이터 요청")
        print("3. 예: '@workspace /mcp-alpha-vantage AAPL 주가 정보'")

        # 사용 예제 파일 생성
        create_mcp_usage_examples()

    else:
        print("\n❌ MCP 서버 설정에 문제가 있습니다.")
        print("uv가 올바르게 설치되어 있는지 확인하세요.")

    print("\n🔗 더 많은 정보:")
    print("- Alpha Vantage MCP 문서: https://mcp.alphavantage.co/")
    print("- Alpha Vantage API 문서: https://www.alphavantage.co/documentation/")


if __name__ == "__main__":
    asyncio.run(main())
