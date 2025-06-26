"""
Simple security scanner using LangGraph Swarm
"""

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore
from langgraph_swarm import create_handoff_tool, create_swarm
from rich.console import Console

from common.config import (
    OPENAI_API_KEY,
    OPENAI_API_MODEL,
    OPENAI_API_URL,
)
from common.prompts import get_prompt_template

from .models import AnalysisResult
from .prompts import (
    ANALYSIS_SYSTEM_PROMPT,
    NETWORK_SYSTEM_PROMPT,
    REQUEST_PROCESSING_PROMPT,
    REQUEST_PROCESSING_SYSTEM_PROMPT,
    SECURITY_SYSTEM_PROMPT,
)

MAX_ATTEMPTS = 3


console = Console()


def create_security_agent():
    llm = ChatOpenAI(
        model=OPENAI_API_MODEL, api_key=OPENAI_API_KEY, base_url=OPENAI_API_URL
    )

    request_processing_agent = create_react_agent(
        llm,
        [
            create_handoff_tool(
                agent_name="network_agent", description="Network scanning agent"
            ),
            create_handoff_tool(
                agent_name="security_agent", description="Security scanning agent"
            ),
            create_handoff_tool(
                agent_name="analysis_agent", description="Data analysis agent"
            ),
        ],
        prompt=REQUEST_PROCESSING_SYSTEM_PROMPT,
        name="request_processing_agent",
    )

    network_agent = create_react_agent(
        llm,
        [
            create_handoff_tool(
                agent_name="request_processing_agent",
                description="Processes user's requests",
            ),
            create_handoff_tool(
                agent_name="security_agent", description="Security scanning agent"
            ),
            create_handoff_tool(
                agent_name="analysis_agent", description="Data analysis agent"
            ),
        ],
        prompt=NETWORK_SYSTEM_PROMPT,
        name="network_agent",
    )

    security_agent = create_react_agent(
        llm,
        [
            create_handoff_tool(
                agent_name="request_processing_agent",
                description="Processes user's requests",
            ),
            create_handoff_tool(
                agent_name="network_agent", description="Network scanning agent"
            ),
            create_handoff_tool(
                agent_name="analysis_agent", description="Data analysis agent"
            ),
        ],
        prompt=SECURITY_SYSTEM_PROMPT,
        name="security_agent",
    )

    analysis_agent = create_react_agent(
        llm,
        [
            create_handoff_tool(
                agent_name="request_processing_agent",
                description="Processes user's requests",
            ),
            create_handoff_tool(
                agent_name="network_agent", description="Network scanning agent"
            ),
            create_handoff_tool(
                agent_name="security_agent", description="Security scanning agent"
            ),
        ],
        prompt=ANALYSIS_SYSTEM_PROMPT,
        name="analysis_agent",
        response_format=AnalysisResult,
    )

    checkpointer = InMemorySaver()
    store = InMemoryStore()
    agent = create_swarm(
        [request_processing_agent, network_agent, security_agent, analysis_agent],
        default_active_agent="request_processing_agent",
    )

    app = agent.compile(checkpointer=checkpointer, store=store)

    return app


async def run_security_scan(host: str) -> AnalysisResult:
    """Run a complete security scan on the given host."""
    agent = create_security_agent()
    template = get_prompt_template(REQUEST_PROCESSING_PROMPT)
    output = await agent.ainvoke({"messages": template.format_messages(host=host)})

    print(output)

    return output
