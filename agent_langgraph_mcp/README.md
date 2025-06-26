# Сканер безопасности на основе LangGraph и инструментов MCP

По сути, является аналогом [agent_langgraph](../agent_langgraph/README.md), только инструменты работают через MCP.

Этот вариант гораздо более расширяемый, так как вы можете подключить любые инструменты через универсальный протокол MCP.
Даже других агентов - смотрите, например, [agent_mcp_swarm](../agent_mcp_swarm/README.md). Волшебство, правда?

## Запуск:

```bash
# в одной консоли
pythom -m agent_langgraph_mcp.server

# в другой консоли
python -m agent_langgraph_mcp.main <цель>
```
