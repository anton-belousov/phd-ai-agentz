"""
Agent entry point
"""

import asyncio
from json import dumps

import typer
from rich.console import Console
from rich.panel import Panel

from .agent import AgentOutputState, run_security_scan

app = typer.Typer()
console = Console()


@app.command()
def scan(
    host: str = typer.Argument(..., help="Host (IP address or domain) to scan"),
):
    """Run a security scan on the specified host."""
    console.print("[bold green]Starting security scan...[/bold green]")

    try:
        console.print(f"[bold blue]Starting security scan for {host}...[/bold blue]")
        result: AgentOutputState = asyncio.run(run_security_scan(host))

        console.print(
            Panel(
                dumps(result["result"].model_dump(), indent=4, ensure_ascii=False),
                title="Analysis",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    app()
