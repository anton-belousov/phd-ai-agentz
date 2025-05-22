from asyncio import create_subprocess_shell, subprocess, wait_for
from json import dumps

import shodan
from langchain_core.tools import tool
from rich.console import Console

from common.config import SHODAN_API_KEY

console = Console()


async def run_command(command: str, timeout: int = 30) -> subprocess.Process:
    """Run a command and return the results."""
    console.print(f"[bold blue]\tRunning {command}...[/bold blue]")

    return await wait_for(
        create_subprocess_shell(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ),
        timeout=timeout,
    )


@tool(description="Ping a given IP address")
async def ping(ip_address: str) -> str:
    """Execute ping command and return results."""
    console.print(f"[bold blue]Pinging {ip_address}...[/bold blue]")

    try:
        result: subprocess.Process = await run_command(
            " ".join(["ping", "-c", "4", ip_address])
        )

        stdout, stderr = await result.communicate()
        return_code = result.returncode

        if return_code != 0:
            return stderr.decode()

        return stdout.decode()

    except Exception as e:
        return str(e)


@tool(description="Traceroute a given IP address")
async def traceroute(ip_address: str) -> str:
    """Execute traceroute command and return results."""
    console.print(f"[bold blue]Tracerouting {ip_address}...[/bold blue]")
    try:
        result: subprocess.Process = await run_command(
            " ".join(["traceroute", ip_address])
        )
        return result.stdout.decode()

    except Exception as e:
        return str(e)


@tool(description="Scan a given IP address with nmap")
async def nmap_scan(ip_address: str) -> str:
    """Execute nmap scan and return results."""
    console.print(f"[bold blue]Scanning {ip_address} with nmap...[/bold blue]")

    try:
        result: subprocess.Process = await run_command(
            " ".join(["nmap", "-sV", ip_address])
        )
        return result.stdout.decode()

    except Exception as e:
        return str(e)


@tool(description="Look up IP address information using Shodan API")
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
