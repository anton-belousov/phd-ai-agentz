"""
MCP сервер инструментов безопасности
"""

from mcp.server.fastmcp import FastMCP

from common.tools import nmap_scan, shodan_lookup

MCP_SERVER_PORT = 8001

mcp = FastMCP("security_tools", port=MCP_SERVER_PORT)


@mcp.tool(description="Scan a given IP address with nmap")
async def nmap_scan_tool(ip_address: str) -> str:
    """
    Выполняет nmap-сканирование и возвращает результат.
    """
    return await nmap_scan(ip_address)


@mcp.tool(description="Look up IP address information using Shodan API")
async def shodan_lookup_tool(ip_address: str) -> str:
    """
    Ищет информацию о IP-адресе с помощью Shodan API.
    """
    return await shodan_lookup(ip_address)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
