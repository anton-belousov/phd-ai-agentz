"""
MCP сервер сетевых инструментов
"""

from mcp.server.fastmcp import FastMCP

from common.tools import nslookup, ping, traceroute

MCP_SERVER_PORT = 8000

mcp = FastMCP("network_tools", port=MCP_SERVER_PORT)


@mcp.tool(description="Get IP address for the given domain")
async def nslookup_tool(domain: str) -> str:
    """
    Выполняет nslookup и возвращает результат.
    """
    return await nslookup(domain)


@mcp.tool(description="Ping a given IP address")
async def ping_tool(ip_address: str) -> str:
    """
    Выполняет ping и возвращает результат.
    """
    return await ping(ip_address)


@mcp.tool(description="Traceroute a given IP address")
async def traceroute_tool(ip_address: str) -> str:
    """
    Выполняет traceroute и возвращает результат.
    """
    return await traceroute(ip_address)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
