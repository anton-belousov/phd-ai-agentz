# Сканер безопасности на основе LangGraph и инструментов MCP

По сути, является аналогом [agent_langgraph](../agent_langgraph/), только инструменты работают через MCP по HTTP.

Этот вариант гораздо более расширяемый, так как вы можете подключить любые инструменты через универсальный протокол MCP.
Даже других агентов - смотрите, например, [agent_mcp_swarm](../agent_mcp_swarm/). Волшебство, правда?

## Запуск:

Из корня репозитория:

```bash
# в одной консоли - для запуска сервера с инструментами
python -m agent_langgraph_mcp.server

# в другой консоли - для запуска агента
python -m agent_langgraph_mcp.main <цель>
```

## Добавление новых инструментов

Добавьте конфиги дополнительных MCP серверов в `agent_langgraph_mcp/agent.py`, константа `MCP_SERVERS`. Например:

```python
MCP_SERVERS = {
    "security": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    },
    "other": {
        "url": "http://localhost:8001/mcp",
        "transport": "streamable_http",
    },
    "fetch": {
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "transport": "stdio",
    },
}
```