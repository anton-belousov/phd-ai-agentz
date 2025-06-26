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

### Конфигурация

1. Скопируйте файл с конфигурацией в `.env`:

      ```bash
      cp env.example .env
      ```

1. Отредактируйте значения переменных в `.env`

## Использование

Смотрите документацию каждого агента для информации о запуске.

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
