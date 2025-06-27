"""
Agent entry point
"""

import asyncio

import typer
from rich.console import Console
from rich.panel import Panel

from .agent import run_security_scan
from .models import AnalysisResult

app = typer.Typer()
console = Console()


@app.command()
def scan(
    host: str = typer.Argument(..., help="Host (IP address or domain) to scan"),
):
    """
    Run a security scan on the specified host.
    """

    console.print("[bold green]Starting security scan...[/bold green]")

    try:
        console.print(f"[bold blue]Starting security scan for {host}...[/bold blue]")
        result: AnalysisResult = asyncio.run(run_security_scan(host))

        console.print(
            Panel(
                result.model_dump_json(indent=4),
                title="Analysis",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    app()
