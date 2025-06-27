"""
MCP сервер
"""

from mcp.server.fastmcp import FastMCP

from common.tools import nmap_scan, nslookup, ping, shodan_lookup, traceroute

mcp = FastMCP("agent_langgraph_mcp")


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
