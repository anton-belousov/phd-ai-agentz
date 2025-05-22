# PHD AI Agentz

Этот проект содержит четыре различные реализации агентов кибербезопасности, использующих разные подходы:
- langgraph: Простой агент на базе LangGraph
- langgraph-swarm: Рой агентов на базе LangGraph
- mcp: Реализация Model Context Protocol
- langgraph-mcp: Комбинированный подход LangGraph и MCP

## Структура проекта

```
├── agent_langgraph/           # Простой агент на базе LangGraph
├── agent_langgraph_mcp/       # Комбинированный подход LangGraph и MCP
├── agent_langgraph_swarm/     # Рой агентов на базе LangGraph
└── agent_mcp/                 # Реализация Model Context Protocol
```

## Установка

1. Установите зависимости:
   ```bash
   poetry install --no-root
   ```

2. Активируйте виртуальное окружение:
   ```bash
   poetry shell
   ```

## Требования

- Python 3.12 или выше
- Poetry для управления зависимостями
- Необходимые системные инструменты:
  - ping
  - traceroute
  - nmap
  - API ключ Shodan

## Использование

Каждый агент может быть запущен из командной строки с IP-адресом в качестве входного параметра:

```bash
python -m <имя-подпроекта>.main <ip-адрес>
```

Например, запуск LangGraph:

```bash
python -m agent_langgraph.main 1.2.3.4
```

## Лицензия

MIT
