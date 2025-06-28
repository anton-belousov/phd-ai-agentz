"""
Agent entry point
"""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel

from common.exceptions import print_exception

from .agent import run_security_scan
from .models import AnalysisResult

app = typer.Typer()
console = Console()


@app.command()
def scan(
    host: str = typer.Argument(..., help="Хост (IP-адрес или домен) для сканирования"),
):
    """
    Выполняет сканирование хоста
    """
    console.print("[bold green]Запуск сканирования[/bold green]")

    try:
        console.print(f"[green]\tЗапуск сканирования для {host}[/green]")
        result: AnalysisResult = asyncio.run(run_security_scan(host))

        console.print(
            Panel(
                result.model_dump_json(indent=4),
                title="Результат",
                border_style="green",
            )
        )

    except Exception as e:
        print_exception(e)


if __name__ == "__main__":
    app()
