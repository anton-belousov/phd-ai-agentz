# PHD AI Agentz

Этот проект содержит различные реализации агентов кибербезопасности, использующих разные подходы.

## Зависимости

- Python 3.12 или выше
- uv для управления зависимостями
- Необходимые системные инструменты:
  - ping
  - traceroute
  - nmap
  - nslookup
- API ключ [Shodan](https://shodan.io) (напишите мне в @antonbelousoff - могу поделиться своим)

## Структура проекта

* [agent_langgraph](agent_langgraph/) - простой сканер безопасности на базе LangGraph
* [agent_langgraph_mcp](agent_langgraph_mcp/) - комбинированный подход LangGraph и MCP
* [agent_langgraph_swarm](agent_langgraph_swarm/) - рой агентов на базе LangGraph
* [agent_mcp_swarm](agent_mcp_swarm/) - рой агентов на базе MCP, агенты как MCP инструменты

## Установка

Установите зависимости:

```bash
uv venv
source .venv/bin/activate
uv sync --active
```

## Использование

Каждый агент может быть запущен из командной строки с IP-адресом или доменом в качестве входного параметра:

```bash
python -m <имя-агента>.main <цель>
```

Например, запуск агента LangGraph:

```bash
python -m agent_langgraph.main 1.2.3.4
```

## Что же использовать в моём проекте?

[Мы](https://киберразведка.рф) используем подход описанный в [agent_langgraph](agent_langgraph/) и [agent_langgraph_mcp](agent_langgraph_mcp/).

Эксперименты с "роями" агентов пока не привели к нужному результату, как и сценарий, где агент является ~~пешкой~~ инструментом в руках другого агента.
Возможно, у вас эти сценарии сработают.

## ВНЕЗАПНЫЙ КОНКУРС!

Подключите [metasploit](https://metasploit.com/) через MCP к агенту [agent_mcp_swarm](agent_mcp_swarm/), чтобы агент умел вызывать сканирование цели с помощью модулей metasploit. 
Можно воспользоваться готовым [MCP сервером](https://github.com/GH05TCREW/MetasploitMCP) или написать простенький свой.

С вас пулл-реквест, с меня секретный приз первому, оформившему работающий PR.

## Лицензия

MIT
