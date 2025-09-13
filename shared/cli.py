"""
CLI 인터페이스

Typer를 사용한 명령행 인터페이스를 제공합니다.
"""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="퀀트 백테스트 앱")
console = Console()

# 서브커맨드 그룹들
data_app = typer.Typer(help="데이터 관리 명령어")
strategy_app = typer.Typer(help="전략 관리 명령어")
backtest_app = typer.Typer(help="백테스트 실행 명령어")
report_app = typer.Typer(help="리포트 생성 명령어")

app.add_typer(data_app, name="data")
app.add_typer(strategy_app, name="strategy")
app.add_typer(backtest_app, name="backtest")
app.add_typer(report_app, name="report")


# =============================================================================
# 데이터 관리 명령어
# =============================================================================


@data_app.command("collect")
def collect_data(
    symbols: str = typer.Argument(..., help="수집할 심볼들 (쉼표로 구분)"),
    full: bool = typer.Option(False, "--full", help="전체 데이터 수집"),
    info: bool = typer.Option(True, "--info/--no-info", help="회사 정보 포함"),
    intraday: bool = typer.Option(False, "--intraday", help="인트라데이 데이터 포함"),
) -> None:
    """주식 데이터 수집"""

    symbol_list = [s.strip().upper() for s in symbols.split(",")]

    console.print(f"[cyan]데이터 수집 시작: {symbol_list}[/cyan]")

    async def run_collection():
        try:
            from services.data_service import DataPipeline

            pipeline = DataPipeline()

            if full:
                results = await pipeline.bulk_update(
                    symbol_list,
                    include_info=info,
                    include_intraday=intraday,
                    outputsize="full",
                )
            else:
                results = await pipeline.incremental_update(symbol_list)

            # 결과 테이블 출력
            table = Table(title="데이터 수집 결과")
            table.add_column("심볼", style="cyan")
            table.add_column("정보", style="green")
            table.add_column("일일", style="green")
            table.add_column("인트라데이", style="green")
            table.add_column("상태", style="yellow")

            for result in results:
                info_status = "✓" if result.get("info_success", False) else "✗"
                daily_status = "✓" if result.get("daily_success", False) else "✗"
                intraday_status = "✓" if result.get("intraday_success", False) else "✗"

                if result.get("up_to_date"):
                    status = "최신"
                elif result.get("daily_success"):
                    status = "완료"
                else:
                    status = "실패"

                table.add_row(
                    result["symbol"], info_status, daily_status, intraday_status, status
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]오류: {e}[/red]")

    asyncio.run(run_collection())


@data_app.command("setup")
def setup_default_data() -> None:
    """기본 종목 데이터 설정"""
    from services.data_service import setup_default_symbols

    console.print("[cyan]기본 종목 데이터 설정 중...[/cyan]")

    async def run_setup():
        try:
            results = await setup_default_symbols()

            success_count = sum(1 for r in results if r.get("daily_success", False))
            total_count = len(results)

            console.print(f"[green]완료: {success_count}/{total_count} 종목 설정됨[/green]")

            # 실패한 종목들 표시
            failed_symbols = [
                r["symbol"] for r in results if not r.get("daily_success", False)
            ]
            if failed_symbols:
                console.print(f"[yellow]실패한 종목: {', '.join(failed_symbols)}[/yellow]")

        except Exception as e:
            console.print(f"[red]오류: {e}[/red]")

    asyncio.run(run_setup())


@data_app.command("list")
def list_data() -> None:
    """저장된 데이터 목록 조회"""
    from services.data_service import DataPipeline

    try:
        pipeline = DataPipeline()
        summary = pipeline.get_data_summary()

        if summary["total_symbols"] == 0:
            console.print("[yellow]저장된 데이터가 없습니다.[/yellow]")
            return

        table = Table(title=f"저장된 데이터 ({summary['total_symbols']}개 종목)")
        table.add_column("심볼", style="cyan")
        table.add_column("시작일", style="green")
        table.add_column("종료일", style="green")
        table.add_column("일수", style="yellow", justify="right")

        for symbol_info in summary["symbols"]:
            start_date = (
                str(symbol_info["start_date"]) if symbol_info["start_date"] else "N/A"
            )
            end_date = (
                str(symbol_info["end_date"]) if symbol_info["end_date"] else "N/A"
            )
            days_count = (
                str(symbol_info["days_count"]) if symbol_info["days_count"] else "N/A"
            )

            table.add_row(
                symbol_info["symbol"],
                start_date,
                end_date,
                days_count,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]오류: {e}[/red]")


@data_app.command("search")
def search_symbol(keywords: str = typer.Argument(..., help="검색 키워드")) -> None:
    """심볼 검색"""
    from services.data_service import AlphaVantageClient

    console.print(f"[cyan]'{keywords}' 검색 중...[/cyan]")

    async def run_search():
        try:
            async with AlphaVantageClient() as client:
                results = await client.search_endpoint(keywords)

                if not results:
                    console.print("[yellow]검색 결과가 없습니다.[/yellow]")
                    return

                table = Table(title="검색 결과")
                table.add_column("심볼", style="cyan")
                table.add_column("이름", style="green")
                table.add_column("지역", style="yellow")
                table.add_column("통화", style="yellow")

                for item in results[:10]:  # 최대 10개만 표시
                    table.add_row(
                        item.get("1. symbol", ""),
                        item.get("2. name", ""),
                        item.get("4. region", ""),
                        item.get("8. currency", ""),
                    )

                console.print(table)

        except Exception as e:
            console.print(f"[red]오류: {e}[/red]")

    asyncio.run(run_search())


# =============================================================================
# 전략 관리 명령어 (향후 구현)
# =============================================================================


@strategy_app.command("list")
def list_strategies() -> None:
    """전략 목록 조회"""
    console.print("[yellow]전략 관리 기능은 향후 구현 예정입니다.[/yellow]")


@strategy_app.command("create")
def create_strategy(name: str = typer.Argument(..., help="전략 이름")) -> None:
    """새 전략 생성"""
    console.print(f"[yellow]전략 '{name}' 생성 기능은 향후 구현 예정입니다.[/yellow]")


# =============================================================================
# 백테스트 명령어 (향후 구현)
# =============================================================================


@backtest_app.command("run")
def run_backtest(
    strategy: str = typer.Argument(..., help="전략 이름"),
    symbols: str = typer.Argument(..., help="심볼들 (쉼표로 구분)"),
    start_date: str = typer.Option("2023-01-01", help="시작일 (YYYY-MM-DD)"),
    end_date: str = typer.Option("2023-12-31", help="종료일 (YYYY-MM-DD)"),
    initial_cash: float = typer.Option(100000.0, help="초기 자본금"),
) -> None:
    """백테스트 실행"""
    console.print("[yellow]백테스트 실행 기능은 향후 구현 예정입니다.[/yellow]")


# =============================================================================
# 리포트 명령어 (향후 구현)
# =============================================================================


@report_app.command("generate")
def generate_report(backtest_id: str = typer.Argument(..., help="백테스트 ID")) -> None:
    """리포트 생성"""
    console.print("[yellow]리포트 생성 기능은 향후 구현 예정입니다.[/yellow]")


# =============================================================================
# 메인 명령어
# =============================================================================


@app.command("version")
def show_version() -> None:
    """버전 정보 표시"""
    console.print("[cyan]퀀트 백테스트 앱 v0.1.0[/cyan]")


@app.command("status")
def show_status() -> None:
    """앱 상태 확인"""
    console.print("[cyan]시스템 상태 확인 중...[/cyan]")

    # 데이터베이스 연결 확인
    try:
        from services.data_service import get_database

        with get_database() as db:
            symbols = db.get_available_symbols()
            console.print(f"[green]✓ 데이터베이스 연결됨 ({len(symbols)}개 종목)[/green]")

    except Exception as e:
        console.print(f"[red]✗ 데이터베이스 연결 실패: {e}[/red]")

    # API 키 확인
    try:
        from shared.config.settings import Settings

        settings = Settings()
        if settings.alphavantage_api_key:
            console.print("[green]✓ Alpha Vantage API 키 설정됨[/green]")
        else:
            console.print("[yellow]⚠ Alpha Vantage API 키 미설정[/yellow]")

    except Exception as e:
        console.print(f"[red]✗ 설정 확인 실패: {e}[/red]")


if __name__ == "__main__":
    app()
