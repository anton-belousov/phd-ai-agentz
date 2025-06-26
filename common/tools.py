"""
Security tools
"""

from asyncio import TimeoutError, create_subprocess_shell, subprocess, wait_for
from json import dumps

import shodan
from rich.console import Console

from common.config import SHODAN_API_KEY

console = Console()


async def _run_command(command: str, timeout: int = 30) -> subprocess.Process:
    """Run a command and return the results."""
    console.print(f"[bold blue]\tRunning {command}...[/bold blue]")

    process: subprocess.Process = await create_subprocess_shell(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    try:
        stdout, stderr = await wait_for(process.communicate(), timeout=timeout)
        return_code = process.returncode

        if return_code != 0:
            return stderr.decode()

        return stdout.decode()

    except TimeoutError:
        console.print(
            f"[bold red]\t\t{command} timed out after {timeout} seconds[/bold red]"
        )
        process.terminate()
        await process.wait()
        raise


async def nslookup(domain: str) -> str:
    """Execute nslookup command and return results."""
    console.print(f"[bold blue]Looking up {domain} with nslookup...[/bold blue]")

    try:
        return await _run_command(" ".join(["nslookup", domain]))

    except Exception as e:
        return str(e)


async def ping(ip_address: str) -> str:
    """Execute ping command and return results."""
    console.print(f"[bold blue]Pinging {ip_address}...[/bold blue]")

    try:
        return await _run_command(" ".join(["ping", "-c", "4", ip_address]))

    except Exception as e:
        return str(e)


async def traceroute(ip_address: str) -> str:
    """Execute traceroute command and return results."""
    console.print(f"[bold blue]Tracerouting {ip_address}...[/bold blue]")
    try:
        return await _run_command(" ".join(["traceroute", ip_address]))

    except Exception as e:
        return str(e)


async def nmap_scan(ip_address: str) -> str:
    """Execute nmap scan and return results."""
    console.print(f"[bold blue]Scanning {ip_address} with nmap...[/bold blue]")

    try:
        return await _run_command(" ".join(["nmap", "-sV", ip_address]))

    except Exception as e:
        return str(e)


async def shodan_lookup(ip_address: str) -> str:
    """Look up IP address information using Shodan API."""
    console.print(f"[bold blue]Looking up {ip_address} with Shodan...[/bold blue]")

    shodan_client = shodan.Shodan(SHODAN_API_KEY) if SHODAN_API_KEY else None

    if not shodan_client:
        raise RuntimeError("Shodan API key not configured")

    try:
        result = shodan_client.host(ip_address)
        return dumps(result["data"][0]["vulns"], indent=4)

    except shodan.APIError as e:
        return str(e)
