"""
Simple security scanner using LangGraph and tools connected via MCP
"""

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from ..agent_langgraph.agent import create_security_agent
from ..agent_langgraph.models import AgentInputState, AgentOutputState, AnalysisResult

SERVER_URL = "http://localhost:8000/mcp"


async def run_security_scan(host: str) -> AnalysisResult:
    """Run a complete security scan on the given host."""

    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools: list[BaseTool] = await load_mcp_tools(session)
            agent = create_security_agent(tools)

            input_state = AgentInputState(host=host)
            output_state: AgentOutputState = await agent.ainvoke(input_state)

            return output_state["result"]
