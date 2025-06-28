"""
Простой сканер безопасности, который использует mcp-agent для выполнения инструментов.
"""

import asyncio
import uuid

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langgraph_swarm import create_handoff_tool, create_swarm
from mcp.server.fastmcp import FastMCP
from rich.console import Console

from common.config import DEBUG_SWARM, OPENAI_API_KEY, OPENAI_API_MODEL, OPENAI_API_URL
from common.prompts import get_prompt_template

from .models import AnalysisResult, CustomSwarmState, ScanTaskStatus
from .prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    NETWORK_SYSTEM_PROMPT,
    REQUEST_PROCESSING_PROMPT,
    REQUEST_PROCESSING_SYSTEM_PROMPT,
    SECURITY_SYSTEM_PROMPT,
)

MCP_SERVER_PORT = 8002

# сервер надо предварительно запустить
MCP_SERVERS = {
    "network_tools": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
    "security_tools": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    },
}

scan_tasks: dict[str, asyncio.Task] = {}
console = Console()
mcp = FastMCP("agent_mcp_swarm", port=MCP_SERVER_PORT)


async def create_security_swarm():
    """
    Создание роя агентов
    """
    llm = ChatOpenAI(
        model=OPENAI_API_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL
    )
    tools_client = MultiServerMCPClient(MCP_SERVERS)
    network_server_tools: list[BaseTool] = await tools_client.get_tools(
        server_name="network_tools"
    )
    security_server_tools: list[BaseTool] = await tools_client.get_tools(
        server_name="security_tools"
    )

    request_procesing_handoff = create_handoff_tool(
        agent_name="request_processing_agent",
        description="Processes user's requests",
    )
    network_handoff = create_handoff_tool(
        agent_name="network_agent", description="Network scanning agent"
    )
    security_handoff = create_handoff_tool(
        agent_name="security_agent", description="Security scanning agent"
    )
    analysis_handoff = create_handoff_tool(
        agent_name="analysis_agent", description="Data analysis agent"
    )

    # выписываем инструменты для каждого агента и вручную добавляем в LLM,
    # потому что в LangGraph Swarm нет поддержки параллельных вызовов инструментов - он не успевает добавить результаты инструментов в очередь сообщений
    # и всё нахрен падает
    request_processing_tools = [
        network_handoff,
        security_handoff,
        analysis_handoff,
    ]
    network_tools = network_server_tools + [
        request_procesing_handoff,
        security_handoff,
        analysis_handoff,
    ]
    security_tools = security_server_tools + [
        request_procesing_handoff,
        network_handoff,
        analysis_handoff,
    ]

    llm_with_request_processing_tools = llm.bind_tools(
        request_processing_tools, parallel_tool_calls=False
    )
    llm_with_network_tools = llm.bind_tools(network_tools, parallel_tool_calls=False)
    llm_with_security_tools = llm.bind_tools(security_tools, parallel_tool_calls=False)

    request_processing_agent = create_react_agent(
        llm_with_request_processing_tools,
        request_processing_tools,
        prompt=REQUEST_PROCESSING_SYSTEM_PROMPT,
        name="request_processing_agent",
        debug=DEBUG_SWARM,
    )

    network_agent = create_react_agent(
        llm_with_network_tools,
        network_tools,
        prompt=NETWORK_SYSTEM_PROMPT,
        name="network_agent",
        debug=DEBUG_SWARM,
    )

    security_agent = create_react_agent(
        llm_with_security_tools,
        security_tools,
        prompt=SECURITY_SYSTEM_PROMPT,
        name="security_agent",
        debug=DEBUG_SWARM,
    )

    analysis_agent = create_react_agent(
        llm,
        [],
        prompt=ANALYSIS_SYSTEM_PROMPT,
        response_format=(ANALYSIS_SYSTEM_PROMPT, AnalysisResult),
        name="analysis_agent",
        debug=DEBUG_SWARM,
    )

    checkpointer = InMemorySaver()
    store = InMemoryStore()
    swarm = create_swarm(
        [request_processing_agent, network_agent, security_agent, analysis_agent],
        default_active_agent="request_processing_agent",
        state_schema=CustomSwarmState,
    )

    app = swarm.compile(checkpointer=checkpointer, store=store)

    return app


async def run_security_scan(host: str) -> AnalysisResult:
    """
    Выполняет сканирование хоста
    """
    console.print("[bold blue]Вызов роя агентов...[/bold blue]")

    swarm = await create_security_swarm()
    template = get_prompt_template(REQUEST_PROCESSING_PROMPT)
    config = {"configurable": {"thread_id": "1"}}

    # CustomSwarmState - это состояние роя, которое мы используем для хранения результатов
    # Нам нужен structured_response из analysis_agent, который содержит результаты сканирования
    # Иначе рой вернёт просто список сообщений, а не структурированный ответ
    output: CustomSwarmState = await swarm.ainvoke(
        {"messages": template.format_messages(host=host)}, config
    )

    assert "structured_response" in output
    assert isinstance(output["structured_response"], AnalysisResult)

    return output["structured_response"]


async def _get_security_scan_status(run_id: str) -> ScanTaskStatus:
    """
    Возвращает статус выполнения сканирования и результат, если он доступен.
    """

    task = scan_tasks.get(run_id)

    if task is None:
        return ScanTaskStatus(run_id=run_id, status="not_found", result=None)

    if not task.done():
        return ScanTaskStatus(run_id=run_id, status="running", result=None)

    if task.cancelled():
        return ScanTaskStatus(run_id=run_id, status="cancelled", result=None)

    try:
        result: AnalysisResult = task.result()
        return ScanTaskStatus(run_id=run_id, status="completed", result=result)

    except Exception as e:
        return ScanTaskStatus(run_id=run_id, status="failed", result=str(e))


@mcp.tool(description="Run security scan against the given host")
async def security_scan_tool(host: str) -> str:
    """
    Запускает сканирование хоста в фоновом режиме и возвращает идентификатор задачи.
    """
    console.print(f"[blue]Запуск сканирования хоста {host}...[/blue]")

    run_id = str(uuid.uuid4())
    task = asyncio.create_task(run_security_scan(host))
    scan_tasks[run_id] = task

    return run_id


@mcp.tool(description="Get status of security scan")
async def security_scan_status_tool(run_id: str) -> ScanTaskStatus:
    """
    Возвращает статус выполнения сканирования и результат, если он доступен.
    """
    console.print(f"[blue]Получение статуса сканирования {run_id}...[/blue]")
    status = await _get_security_scan_status(run_id)
    console.print(f"[blue]\t- Статус сканирования {run_id}: {status.status}[/blue]")

    return status


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
