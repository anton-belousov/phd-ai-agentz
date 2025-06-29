# PHD AI Agentz

Различные реализации агентов - сканеров сетевой конфигурации и кибербезопасности, использующих разные подходы.

## Зависимости

- Linux или Mac OS, на Windows скорее всего работать не будет
- Python 3.12 или выше
- uv для управления зависимостями
- Необходимые системные инструменты:
  - ping
  - traceroute
  - nmap
  - nslookup
- API ключ [Shodan](https://shodan.io) (напишите мне - могу поделиться своим)

## Структура проекта

* [agent_langgraph](agent_langgraph/) - простой сканер безопасности на базе LangGraph
* [agent_langgraph_mcp](agent_langgraph_mcp/) - комбинированный подход LangGraph и MCP
* [agent_langgraph_swarm](agent_langgraph_swarm/) - рой агентов на базе LangGraph Swarm
* [agent_mcp_swarm](agent_mcp_swarm/) - рой агентов на базе LangGraph Swarm, который в свою очередь обёрнут в свой MCP-сервер для использования в других MCP-клиентах

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

## Что же использовать в своём проекте?

[Мы](https://киберразведка.рф) используем подход описанный в [agent_langgraph](agent_langgraph/) и [agent_langgraph_mcp](agent_langgraph_mcp/).

Эксперименты с "роями" агентов пока не привели к нужному результату, как и сценарий, где агент является ~~пешкой~~ инструментом в руках другого агента.
Возможно, у вас эти сценарии сработают.

## ВНЕЗАПНЫЙ КОНКУРС (или домашнее задание)!

Подключите [openvas](https://github.com/greenbone/openvas-scanner) или [metasploit](https://metasploit.com/) через MCP к агенту [agent_mcp_swarm](agent_mcp_swarm/) или [agent_langgraph_mcp](agent_langgraph_mcp/), чтобы агент умел вызывать сканирование уязвимостей цели и выводить репорт в результатах.

С вас работающий пулл-реквест, с меня 10 000 рублей на СБП первому, кто справится. Если кто-то вдруг решится, напишите, пожалуйста в Телеграм.

## Лицензия

MIT

## Контакты

Telegram: @antonbelousoff
