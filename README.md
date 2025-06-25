# PHD AI Agentz

Этот проект содержит четыре различные реализации агентов кибербезопасности, использующих разные подходы:
- langgraph: Простой агент на базе LangGraph
- langgraph-mcp: Комбинированный подход LangGraph и MCP
- langgraph-swarm: Рой агентов на базе LangGraph
- mcp: Реализация Model Context Protocol

Все проекты реализуют простой сканер безопасности и сетевой конфигурации удалённого сервера - комбинацию утилит nmap, shodan, ping, nslookup, traceroute.

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
  - nslookup
- API ключ Shodan (напишите мне в @antonbelousoff - могу поделиться своим)

## Использование

Каждый агент может быть запущен из командной строки с IP-адресом или доменом в качестве входного параметра:

```bash
python -m <имя-подпроекта>.main <хост>
```

1. запуск агента LangGraph:

   ```bash
   python -m agent_langgraph.main 1.2.3.4
   ```

2. запуск агента LangGraph-MCP:

   ```bash
   python -m agent_langgraph_mcp.main 1.2.3.4
   ```

3. запуск агента LangGraph-Swarm:

   ```bash
   python -m agent_langgraph_swarm.main 1.2.3.4
   ```

4. запуск агента MCP:

   ```bash
   python -m agent_mcp.main 1.2.3.4
   ```

## Домашнее задание

Подключите MCP Metasploit к агенту LangGraph-MCP, чтобы бот умел вызывать сканирование с помощью модулей metasploit. Можно воспользоваться готовым [MCP сервером](https://github.com/GH05TCREW/MetasploitMCP) или написать простенький свой.

С вас пулл-реквест, с меня секретный приз первому, оформившему рабочий PR.

## Лицензия

MIT
