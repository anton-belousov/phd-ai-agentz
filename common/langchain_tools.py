"""
LangChain инструменты
"""

from langchain_core.tools import tool

from .tools import nmap_scan, nslookup, ping, shodan_lookup, traceroute


@tool(description="Get IP address for the given domain")
async def nslookup_tool(domain: str) -> str:
    """
    Выполняет nslookup и возвращает результат.
    """
    return await nslookup(domain)


@tool(description="Ping a given IP address")
async def ping_tool(ip_address: str) -> str:
    """
    Выполняет ping и возвращает результат.
    """
    return await ping(ip_address)


@tool(description="Traceroute a given IP address")
async def traceroute_tool(ip_address: str) -> str:
    """
    Выполняет traceroute и возвращает результат.
    """
    return await traceroute(ip_address)


@tool(description="Scan a given IP address with nmap")
async def nmap_scan_tool(ip_address: str) -> str:
    """
    Выполняет nmap-сканирование и возвращает результат.
    """
    return await nmap_scan(ip_address)


@tool(description="Look up IP address information using Shodan API")
async def shodan_lookup_tool(ip_address: str) -> str:
    """
    Ищет информацию о IP-адресе с помощью Shodan API.
    """
    return await shodan_lookup(ip_address)
