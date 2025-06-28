"""
Инструменты для сканирования
"""

from asyncio import TimeoutError, create_subprocess_shell, subprocess, wait_for
from json import dumps

import shodan
from rich.console import Console
from rich.panel import Panel

from common.config import PRINT_TOOL_RESULTS, SHODAN_API_KEY

console = Console()


async def _run_command(command: str, timeout: int = 30) -> subprocess.Process:
    """
    Выполняет команду и возвращает результат.
    """
    console.print(f"[magenta]\t\tВыполнение команды: {command}[/magenta]")

    process: subprocess.Process = await create_subprocess_shell(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    result: str | None = None

    try:
        stdout, stderr = await wait_for(process.communicate(), timeout=timeout)
        return_code = process.returncode

        if return_code != 0:
            error_result: str | None = stderr.decode()

            if not error_result:
                error_result = "Error running command"

            result = error_result
        else:
            result = stdout.decode()

    except TimeoutError:
        console.print(
            f"[red]\t\t{command} завершилась по таймауту {timeout} секунд[/red]"
        )
        process.terminate()
        await process.wait()

        raise RuntimeError("Command has timed out")

    if PRINT_TOOL_RESULTS:
        console.print(Panel(result, title="Результат", border_style="magenta"))

    return result


async def nslookup(domain: str) -> str:
    """
    Выполняет nslookup и возвращает результат.
    """
    console.print(f"[magenta]\t\tПоиск {domain} с помощью nslookup[/magenta]")

    try:
        return await _run_command(" ".join(["nslookup", domain]))

    except Exception as e:
        return str(e)


async def ping(ip_address: str) -> str:
    """
    Выполняет ping и возвращает результат.
    """
    console.print(f"[magenta]\t\tПинг {ip_address}[/magenta]")

    try:
        return await _run_command(" ".join(["ping", "-c", "4", ip_address]))

    except Exception as e:
        return str(e)


async def traceroute(ip_address: str) -> str:
    """
    Выполняет traceroute и возвращает результат.
    """
    console.print(f"[magenta]\t\tТрассировка {ip_address}[/magenta]")

    try:
        return await _run_command(
            " ".join(["traceroute", "-w", "1", "-q", "1", "-m", "20", ip_address]),
            timeout=60,
        )

    except Exception as e:
        return str(e)


async def nmap_scan(ip_address: str) -> str:
    """
    Выполняет nmap-сканирование и возвращает результат.
    """
    console.print(f"[magenta]\t\tСканирование {ip_address} с помощью nmap[/magenta]")

    try:
        return await _run_command(
            " ".join(["nmap", "-sV", "-v", "-A", "-T4", "-Pn", ip_address]), timeout=60
        )

    except Exception as e:
        return str(e)


async def shodan_lookup(ip_address: str) -> str:
    """
    Ищет информацию о IP-адресе с помощью Shodan API.
    """
    console.print(f"[magenta]\t\tПоиск {ip_address} с помощью Shodan[/magenta]")

    shodan_client = shodan.Shodan(SHODAN_API_KEY) if SHODAN_API_KEY else None

    if not shodan_client:
        raise RuntimeError("Shodan API ключ не настроен")

    try:
        result = shodan_client.host(ip_address)
        return dumps(result["data"][0]["vulns"], indent=4)

    except shodan.APIError as e:
        return str(e)
