"""
Simple security scanner using LangGraph and tools connected via MCP
"""

# Create server parameters for stdio connection
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from common.config import OPENAI_API_MODEL

from .models import AnalysisResult
from .prompts import FIRST_PROMPT

SERVER_URL = "http://localhost:8000/mcp"


async def run_security_scan(host: str) -> AnalysisResult:
    """Run a complete security scan on the given host."""

    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools: list[BaseTool] = await load_mcp_tools(session)
            agent = create_react_agent(
                OPENAI_API_MODEL, tools, response_format=AnalysisResult
            )

            messages: list[BaseMessage] = ChatPromptTemplate.from_template(
                FIRST_PROMPT
            ).format_messages(host=host)

            result: AnalysisResult = await agent.ainvoke({"messages": messages})
            print(result)

            return result
