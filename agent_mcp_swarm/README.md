# Сканер безопасности на основе LangGraph Swarm, обёрнутый в инструмент MCP

Является копией [agent_langgraph_swarm](../agent_langgraph_swarm/), но инструменты запускаются в отдельных серверах MCP и сам агент обёрнут в сервер MCP, чтобы добавить жести.

## Запуск:

Тут придётся запустить 4 программы - 2 MCP-сервера с инструментами, MCP-сервер с роем агентов и клиента (основную программу).

Из корня репозитория:

```bash
# сервер с сетевыми инструментами
python -m agent_mcp_swarm.network_tools_server

# сервер с инструментами безопасности
python -m agent_mcp_swarm.security_tools_server

# сервер с роем агентов
python -m agent_mcp_swarm.agent_server

# главная комманда
python -m agent_mcp_swarm.main <цель>
```

![langgraph.gif](../images/mcp_swarm.gif)

## Примечания

* Возможно, вместо этого варианта стоит попробовать [A2A](https://github.com/a2aproject/A2A) - его ещё не смотрел. На первый взгляд выглядит так, что для межагентского взаимодействия оно подходит лучше MCP.
