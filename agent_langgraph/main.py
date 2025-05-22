import asyncio
from json import dumps

import typer
from rich.console import Console
from rich.panel import Panel

from .agent import AgentOutputState, run_security_scan

app = typer.Typer()
console = Console()


def validate_ip(ip: str) -> bool:
    """Basic IP address validation."""
    parts = ip.split(".")
    return len(parts) == 4 and all(
        part.isdigit() and 0 <= int(part) <= 255 for part in parts
    )


@app.command()
def scan(
    ip_address: str = typer.Argument(..., help="IP address to scan"),
):
    """Run a security scan on the specified IP address."""
    console.print("[bold green]Starting security scan...[/bold green]")

    if not validate_ip(ip_address):
        console.print("[red]Error: Invalid IP address format[/red]")
        raise typer.Exit(1)

    try:
        console.print(
            f"[bold blue]Starting security scan for {ip_address}...[/bold blue]"
        )
        result: AgentOutputState = asyncio.run(run_security_scan(ip_address))

        console.print(
            Panel(
                dumps(result, indent=4),
                title="Analysis",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise


if __name__ == "__main__":
    app()
