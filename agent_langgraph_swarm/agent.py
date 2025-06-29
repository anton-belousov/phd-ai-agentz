"""
Простой сканер безопасности, который использует LangGraph Swarm для выполнения инструментов.
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langgraph_swarm import create_handoff_tool, create_swarm
from rich.console import Console

from common.config import (
    DEBUG_SWARM,
    OPENAI_API_KEY,
    OPENAI_API_MODEL,
    OPENAI_API_URL,
)
from common.langchain_tools import (
    nmap_scan_tool,
    nslookup_tool,
    ping_tool,
    shodan_lookup_tool,
    traceroute_tool,
)
from common.langfuse import get_callback_handler
from common.prompts import get_prompt_template

from .models import AnalysisResult, CustomSwarmState
from .prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    NETWORK_SYSTEM_PROMPT,
    REQUEST_PROCESSING_PROMPT,
    REQUEST_PROCESSING_SYSTEM_PROMPT,
    SECURITY_SYSTEM_PROMPT,
)

console = Console()


def create_security_swarm():
    """
    Создание роя агентов
    https://www.youtube.com/watch?v=tx6wJcVQRp8 (извините)
    """
    llm = ChatOpenAI(
        model=OPENAI_API_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL
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
    network_tools = [
        nslookup_tool,
        ping_tool,
        traceroute_tool,
        request_procesing_handoff,
        security_handoff,
        analysis_handoff,
    ]
    security_tools = [
        shodan_lookup_tool,
        nmap_scan_tool,
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

    app = swarm.compile(checkpointer=checkpointer, store=store).with_config(
        {"run_name": "agent_langgraph_swarm"}
    )

    return app


async def run_security_scan(host: str) -> AnalysisResult:
    """
    Выполняет сканирование хоста
    """
    console.print("[bold blue]Вызов роя агентов...[/bold blue]")

    swarm = create_security_swarm()
    template = get_prompt_template(REQUEST_PROCESSING_PROMPT)
    config = {"configurable": {"thread_id": "1"}, "callbacks": [get_callback_handler()]}

    # CustomSwarmState - это состояние роя, которое мы используем для хранения результатов
    # Нам нужен structured_response из analysis_agent, который содержит результаты сканирования
    # Иначе рой вернёт просто список сообщений, а не структурированный ответ
    output: CustomSwarmState = await swarm.ainvoke(
        {"messages": template.format_messages(host=host)}, config
    )

    assert "structured_response" in output
    assert isinstance(output["structured_response"], AnalysisResult)

    return output["structured_response"]
