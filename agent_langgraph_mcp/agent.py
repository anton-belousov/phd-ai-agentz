"""
Simple security scanner using LangGraph and tools connected via MCP
"""

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from agent_langgraph.agent import create_security_agent
from agent_langgraph.models import AgentInputState, AgentOutputState, AnalysisResult

MCP_SERVERS = {
    "security": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    }
}


async def run_security_scan(host: str) -> AnalysisResult:
    """Run a complete security scan on the given host."""

    client = MultiServerMCPClient(MCP_SERVERS)
    tools: list[BaseTool] = await client.get_tools()
    agent = create_security_agent(tools)

    input_state = AgentInputState(host=host)
    output_state: AgentOutputState = await agent.ainvoke(input_state)

    return output_state["result"]
