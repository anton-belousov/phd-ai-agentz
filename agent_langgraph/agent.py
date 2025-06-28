"""
Простой сканер безопасности, который использует LangGraph для выполнения инструментов.
"""

from typing import Literal

from langchain_core.messages import AIMessage, AnyMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.pregel import RetryPolicy
from rich.console import Console

from common.config import (
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

from .models import AgentInputState, AgentOutputState, AgentState, AnalysisResult
from .prompts import AGENT_PROMPT, ANALYSIS_PROMPT, SUBSEQUENT_PROMPT, SYSTEM_PROMPT

MAX_ATTEMPTS = 3


console = Console()


def create_security_agent(tools: list[BaseTool]):
    """
    Создание агента
    """
    llm = ChatOpenAI(
        model=OPENAI_API_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL
    )
    tool_name_to_tool: dict[str, BaseTool] = {tool.name: tool for tool in tools}

    async def agent(state: AgentState) -> AgentState:
        """
        Вызов агента
        """
        console.print("[blue]\tВызов агента[/blue]")
        host = state["host"]

        messages: list[AnyMessage] = state["messages"]
        new_messages: list[AnyMessage] = []

        if not messages:
            new_messages = get_prompt_template(
                AGENT_PROMPT, SYSTEM_PROMPT
            ).format_messages(host=host)

        else:
            new_messages = get_prompt_template(SUBSEQUENT_PROMPT).format_messages()

        response: AIMessage = await llm.bind_tools(tools).ainvoke(
            messages + new_messages
        )
        new_messages.append(response)

        return AgentState(messages=new_messages)

    async def should_continue(
        state: AgentState,
    ) -> Literal["call_tool", "analyze_results"]:
        """
        Проверяет, нужно ли продолжать выполнение инструментов
        """
        console.print("[blue]\tПроверка необходимости продолжения[/blue]")

        messages: list[AnyMessage] = state["messages"]
        last_message: AnyMessage = messages[-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "call_tool"

        return "analyze_results"

    async def call_tool(state: AgentState) -> AgentState:
        """
        Вызов инструмента
        """
        console.print("[blue]\tВызов инструмента[/blue]")

        messages: list[AnyMessage] = state["messages"]
        last_message: AIMessage = messages[-1]
        new_messages: list[AnyMessage] = []

        for tool_call in last_message.tool_calls:
            console.print(f"[blue]\t\tВызов инструмента: {tool_call['name']}[/blue]")
            tool: BaseTool | None = tool_name_to_tool.get(tool_call["name"])

            if not tool:
                console.print(
                    f"[red]\t\tИнструмент не найден: {tool_call['name']}[/red]"
                )
                continue

            tool_message: ToolMessage = await tool.ainvoke(tool_call)
            new_messages.append(tool_message)

        return AgentState(messages=new_messages)

    async def analyze_results(state: AgentState) -> AgentOutputState:
        """
        Анализирует результаты всех инструментов и предоставляет результат.
        """
        console.print("[blue]\tАнализ результатов[/blue]")

        messages = state["messages"] + get_prompt_template(
            ANALYSIS_PROMPT
        ).format_messages(host=state["host"])

        response: AnalysisResult = await llm.with_structured_output(
            AnalysisResult
        ).ainvoke(messages)

        return AgentOutputState(result=response)

    graph = StateGraph(AgentState, input=AgentInputState, output=AgentOutputState)
    graph.add_node("agent", agent, retry=RetryPolicy(max_attempts=MAX_ATTEMPTS))
    graph.add_node("call_tool", call_tool, retry=RetryPolicy(max_attempts=MAX_ATTEMPTS))
    graph.add_node(
        "analyze_results", analyze_results, retry=RetryPolicy(max_attempts=MAX_ATTEMPTS)
    )

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent", should_continue, ["call_tool", "analyze_results"]
    )
    graph.add_edge("call_tool", "agent")
    graph.add_edge("analyze_results", END)

    return graph.compile().with_config({"run_name": "agent_langgraph"})


async def run_security_scan(host: str) -> AnalysisResult:
    """
    Выполняет сканирование хоста
    """
    console.print("[bold blue]Запуск агента[/bold blue]")

    agent = create_security_agent(
        [
            ping_tool,
            traceroute_tool,
            nmap_scan_tool,
            shodan_lookup_tool,
            nslookup_tool,
        ]
    )
    input_state = AgentInputState(host=host)
    output_state: AgentOutputState = await agent.ainvoke(
        input_state,
        config={
            "callbacks": [get_callback_handler()],
        },
    )

    return output_state["result"]
