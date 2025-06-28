"""
Входная точка для запуска роя
"""

import asyncio
import json
import logging

import typer
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult
from rich.console import Console
from rich.panel import Panel

from .agent_server import MCP_SERVER_PORT

AGENT_URL = f"http://localhost:{MCP_SERVER_PORT}/mcp"

logging.basicConfig(level=logging.ERROR)
app = typer.Typer()
console = Console()


def _print_exception(e: Exception):
    """
    Выводит ошибку в консоль
    """
    if isinstance(e, ExceptionGroup):
        for exc in e.exceptions:
            _print_exception(exc)
    else:
        console.print(Panel(str(e), title="Ошибка", border_style="red"))


def _tool_result_to_json(tool_result: CallToolResult) -> dict | None:
    """
    Преобразует результат вызова инструмента в JSON
    """
    if tool_result.content and len(tool_result.content) > 0:
        text = tool_result.content[0].text

        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return None


async def run_security_scan(host: str) -> dict:
    """
    Выполняет сканирование хоста
    """
    console.print("[blue]\tСоединение с агентом...[/blue]")
    result: dict | None = None

    async with streamablehttp_client(AGENT_URL) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            console.print("[blue]\tСписок доступных инструментов:[/blue]")

            for tool in tools.tools:
                console.print(f"[blue]\t\t- {tool.name}[/blue]")

            run_result: CallToolResult = await session.call_tool(
                "security_scan_tool", arguments={"host": host}
            )

            if run_result.isError:
                raise RuntimeError(
                    f"Вызов агента завершён с ошибкой: {run_result.content[0].text}"
                )

            run_id: str = run_result.content[0].text

            console.print(f"[blue]\tЗапущен агент: {run_id}[/blue]")

            # ждём завершения агента
            while True:
                get_status_result: CallToolResult = await session.call_tool(
                    "security_scan_status_tool",
                    arguments={"run_id": run_id},
                )

                if get_status_result.isError:
                    raise RuntimeError(
                        f"Проверка статуса агента завершилась с ошибкой: {get_status_result.content[0].text}"
                    )

                run_status = _tool_result_to_json(get_status_result)

                if run_status is None or not run_status.get("status"):
                    raise RuntimeError(
                        "Не удалось разобрать результат вызова инструмента"
                    )

                console.print(
                    f"[blue]\tСтатус агента: {run_status.get('status')}[/blue]"
                )
                status: str = run_status.get("status")

                match status:
                    case "completed":
                        console.print(f"[blue]\tАгент завершен: {run_status}[/blue]")
                        result = run_status.get("result")
                        break

                    case "failed":
                        raise RuntimeError(f"Агент завершен с ошибкой: {run_status}")

                    case "running":
                        console.print("[blue]\t\tАгент выполняется...[/blue]")

                    case "cancelled":
                        raise RuntimeError(f"Агент отменен: {run_status}")

                    case _:
                        raise RuntimeError(f"Неизвестный статус: {run_status}")

                await asyncio.sleep(5)

        assert result is not None
        assert isinstance(result, dict)

    return result


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
        result: dict = asyncio.run(run_security_scan(host))

        console.print(
            Panel(
                json.dumps(result, indent=4, ensure_ascii=False),
                title="Результат",
                border_style="green",
            )
        )

    except Exception as e:
        _print_exception(e)


if __name__ == "__main__":
    app()
