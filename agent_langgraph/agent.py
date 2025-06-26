"""
Simple security scanner using LangGraph
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
from common.prompts import get_prompt_template

from .models import AgentInputState, AgentOutputState, AgentState, AnalysisResult
from .prompts import ANALYSIS_PROMPT, FIRST_PROMPT, SUBSEQUENT_PROMPT, SYSTEM_PROMPT

MAX_ATTEMPTS = 3


console = Console()
all_tools = {
    "ping_tool": ping_tool,
    "traceroute_tool": traceroute_tool,
    "nmap_scan_tool": nmap_scan_tool,
    "shodan_lookup_tool": shodan_lookup_tool,
    "nslookup_tool": nslookup_tool,
}


def create_security_agent():
    llm = ChatOpenAI(
        model=OPENAI_API_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL
    )

    async def run_security_tools(state: AgentState) -> AgentState:
        """Run security tools on the IP address."""
        console.print("[bold blue]Running security tools...[/bold blue]")
        console.print(f"state.messages: {len(state['messages'])}")
        host = state["host"]

        messages: list[AnyMessage] = state["messages"]
        new_messages: list[AnyMessage] = []

        if not messages:
            new_messages = get_prompt_template(
                FIRST_PROMPT, SYSTEM_PROMPT
            ).format_messages(host=host)

        else:
            new_messages = get_prompt_template(SUBSEQUENT_PROMPT).format_messages()

        response: AIMessage = await llm.bind_tools(all_tools.values()).ainvoke(
            messages + new_messages
        )
        new_messages.append(response)

        return AgentState(messages=new_messages)

    async def should_continue(
        state: AgentState,
    ) -> Literal["call_tool", "analyze_results"]:
        """Should continue check"""
        console.print("[bold blue]Should continue check...[/bold blue]")

        messages: list[AnyMessage] = state["messages"]
        last_message: AnyMessage = messages[-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "call_tool"

        return "analyze_results"

    async def call_tool(state: AgentState) -> AgentState:
        """Call tool"""
        console.print("[bold blue]Calling tool...[/bold blue]")

        messages: list[AnyMessage] = state["messages"]
        last_message: AIMessage = messages[-1]
        new_messages: list[AnyMessage] = []

        for tool_call in last_message.tool_calls:
            console.print(
                f"[bold blue]Calling tool: {tool_call['name']}...[/bold blue]"
            )
            tool: BaseTool | None = all_tools.get(tool_call["name"])

            if not tool:
                console.print(f"[red]Tool not found: {tool_call['name']}[/red]")
                continue

            tool_message: ToolMessage = await tool.ainvoke(tool_call)
            new_messages.append(tool_message)

        return AgentState(messages=new_messages)

    async def analyze_results(state: AgentState) -> AgentOutputState:
        """Analyze the results from all tools and provide insights."""
        console.print("[bold blue]Analyzing results...[/bold blue]")

        messages = state["messages"] + get_prompt_template(
            ANALYSIS_PROMPT
        ).format_messages(host=state["host"])

        response: AnalysisResult = await llm.with_structured_output(
            AnalysisResult
        ).ainvoke(messages)

        return AgentOutputState(result=response)

    graph = StateGraph(AgentState, input=AgentInputState, output=AgentOutputState)
    graph.add_node(
        "run_security_tools",
        run_security_tools,
        retry=RetryPolicy(max_attempts=MAX_ATTEMPTS),
    )
    graph.add_node("call_tool", call_tool, retry=RetryPolicy(max_attempts=MAX_ATTEMPTS))
    graph.add_node(
        "analyze_results", analyze_results, retry=RetryPolicy(max_attempts=MAX_ATTEMPTS)
    )

    graph.add_edge(START, "run_security_tools")
    graph.add_conditional_edges(
        "run_security_tools",
        should_continue,
        ["call_tool", "analyze_results"],
    )
    graph.add_edge("call_tool", "run_security_tools")
    graph.add_edge("analyze_results", END)

    return graph.compile()


async def run_security_scan(host: str) -> AgentOutputState:
    """Run a complete security scan on the given host."""
    agent = create_security_agent()
    input_state = AgentInputState(host=host)
    output_state: AgentOutputState = await agent.ainvoke(input_state)

    return output_state
