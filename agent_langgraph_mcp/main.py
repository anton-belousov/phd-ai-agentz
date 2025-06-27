"""
Точка входа для агента
"""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel

from agent_langgraph.models import AnalysisResult

from .agent import run_security_scan

app = typer.Typer()
console = Console()


@app.command()
def scan(
    host: str = typer.Argument(..., help="Хост (IP-адрес или домен) для сканирования"),
):
    """
    Выполняет сканирование хоста
    """
    console.print("[bold green]Запуск сканирования...[/bold green]")

    try:
        console.print(f"[bold blue]\tЗапуск сканирования для {host}...[/bold blue]")
        result: AnalysisResult = asyncio.run(run_security_scan(host))

        console.print(
            Panel(
                result.model_dump_json(indent=4),
                title="Результат",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]\tОшибка: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    app()
