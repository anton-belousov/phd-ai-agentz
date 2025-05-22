from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.pregel import RetryPolicy
from pydantic import BaseModel, Field
from rich.console import Console

from common.config import (
    OPENAI_API_KEY,
    OPENAI_API_MODEL,
    OPENAI_API_URL,
)
from common.tools import nmap_scan, ping, shodan_lookup, traceroute

MAX_ATTEMPTS = 3


class AgentInputState(TypedDict):
    ip_address: str


class AgentOutputState(TypedDict):
    has_security_issues: bool
    identified_issues: list[str]


class AgentState(AgentInputState, AgentOutputState):
    messages: Annotated[list[HumanMessage | AIMessage], add_messages]


class AnalysisResult(BaseModel):
    has_security_issues: bool = Field(
        description="Whether the IP address has security issues"
    )
    identified_issues: list[str] = Field(
        description="A list of identified security issues"
    )


console = Console()
all_tools = {
    "ping": ping,
    "traceroute": traceroute,
    "nmap_scan": nmap_scan,
    "shodan_lookup": shodan_lookup,
}


def create_security_agent():
    llm = ChatOpenAI(
        model=OPENAI_API_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL
    )

    async def run_security_tools(state: AgentState) -> AgentState:
        """Run security tools on the IP address."""
        console.print("[bold blue]Running security tools...[/bold blue]")
        console.print(f"state.messages: {len(state['messages'])}")
        ip_address = state["ip_address"]

        messages = state["messages"]
        new_messages = []

        if not messages:
            new_messages = [
                HumanMessage(
                    content=f"Analyze this IP address for security problems: {ip_address}\nUse any 1 tool of your choice to help you. First check if the IP address is reachable using ping. Answer 'done' if you are finished."
                )
            ]

        else:
            new_messages = [
                HumanMessage(
                    content="Use any 1 tool of your choice to help you. Answer 'done' if you are finished."
                )
            ]

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

        messages = state["messages"] + [
            HumanMessage(
                content=f"Analyze these security scan results for the IP address {state['ip_address']} and decide whether it has security issues or not."
            )
        ]

        response: AnalysisResult = await llm.with_structured_output(
            AnalysisResult
        ).ainvoke(messages)

        return AgentOutputState(
            has_security_issues=response.has_security_issues,
            identified_issues=response.identified_issues,
        )

        return state

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


async def run_security_scan(ip_address: str) -> AgentOutputState:
    """Run a complete security scan on the given IP address."""
    agent = create_security_agent()
    input_state = AgentInputState(ip_address=ip_address)
    output_state: AgentOutputState = await agent.ainvoke(input_state)

    return output_state
