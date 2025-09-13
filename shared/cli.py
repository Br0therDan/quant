"""
Quant Backtest App CLI

Typer 기반의 명령줄 인터페이스
각 서비스의 기능을 통합하여 사용자 친화적인 CLI를 제공합니다.
"""

import typer
from rich.console import Console

app = typer.Typer(
    name="quant",
    help="Alpha Vantage 기반 퀀트 백테스트 앱",
    add_completion=False,
)
console = Console()

# 서브커맨드 앱들
data_app = typer.Typer(name="data", help="데이터 관리 명령어")
strategy_app = typer.Typer(name="strategy", help="전략 관리 명령어")
backtest_app = typer.Typer(name="backtest", help="백테스트 실행 명령어")
report_app = typer.Typer(name="report", help="리포트 생성 명령어")

app.add_typer(data_app)
app.add_typer(strategy_app)
app.add_typer(backtest_app)
app.add_typer(report_app)


@data_app.command("fetch")
def fetch_data(
    symbol: str = typer.Argument(..., help="주식 심볼 (예: AAPL)"),
    interval: str = typer.Option("daily", help="데이터 간격 (daily, weekly, monthly)"),
    period: str = typer.Option("1y", help="데이터 기간 (1y, 2y, 5y)"),
) -> None:
    """Alpha Vantage API를 통해 시장 데이터를 수집합니다."""
    console.print(f"[green]데이터 수집 시작[/green]: {symbol} ({interval}, {period})")
    # TODO: data-service 호출
    console.print("[green]✓[/green] 데이터 수집 완료")


@strategy_app.command("create")
def create_strategy(
    template: str = typer.Option(..., help="전략 템플릿 (sma_cross, rsi, momentum)"),
    symbol: str = typer.Option(..., help="대상 심볼"),
    params: str | None = typer.Option(None, help="전략 파라미터 (JSON 형태)"),
) -> None:
    """전략 템플릿을 기반으로 새로운 전략을 생성합니다."""
    console.print(f"[green]전략 생성[/green]: {template} for {symbol}")
    # TODO: strategy-service 호출
    console.print("[green]✓[/green] 전략 생성 완료")


@backtest_app.command("run")
def run_backtest(
    strategy: str = typer.Argument(..., help="실행할 전략 이름"),
    start: str = typer.Option(..., help="백테스트 시작일 (YYYY-MM-DD)"),
    end: str = typer.Option(..., help="백테스트 종료일 (YYYY-MM-DD)"),
    capital: float = typer.Option(100000, help="초기 자본금"),
) -> None:
    """전략을 기반으로 백테스트를 실행합니다."""
    console.print(f"[green]백테스트 실행[/green]: {strategy} ({start} ~ {end})")
    # TODO: backtest-service 호출
    console.print("[green]✓[/green] 백테스트 완료")


@report_app.command("show")
def show_report(
    backtest_id: str = typer.Argument(..., help="백테스트 ID"),
    format: str = typer.Option("table", help="출력 형식 (table, json)"),
) -> None:
    """백테스트 결과 리포트를 표시합니다."""
    console.print(f"[green]리포트 생성[/green]: {backtest_id} ({format})")
    # TODO: analytics-service 호출
    console.print("[green]✓[/green] 리포트 표시 완료")


@app.command("version")
def version() -> None:
    """앱 버전 정보를 표시합니다."""
    console.print("[bold blue]Quant Backtest App[/bold blue] v0.1.0")


if __name__ == "__main__":
    app()
