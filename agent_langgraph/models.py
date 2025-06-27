"""
Модели данных для агента
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class WebApp(BaseModel):
    """
    Веб-приложение.
    """

    name: str = Field(description="Название веб-приложения")
    info: str = Field(description="Информация о веб-приложении")


class AnalysisResult(BaseModel):
    """
    Результат сканирования безопасности хоста.
    """

    has_security_issues: bool = Field(
        description="Наличие проблем безопасности на хосте"
    )
    identified_issues: list[str] = Field(
        description="Список идентифицированных проблем безопасности"
    )
    ip_addresses: list[str] = Field(description="Список IP-адресов хоста")
    ports: list[str] = Field(description="Список открытых портов на хосте")
    services: list[str] = Field(description="Список сервисов, запущенных на хосте")
    network_info: str = Field(
        description="Сетевая информация о хосте - IP-адрес, пинг, трассировка, и т.д."
    )
    os_info: str = Field(description="Информация о операционной системе хоста")
    web_apps: list[WebApp] = Field(
        description="Список веб-приложений, запущенных на хосте"
    )
    ssl_info: str = Field(description="Информация о SSL-сертификатах на хосте")
    other_information: str = Field(description="Другая информация о хосте")


class AgentInputState(TypedDict):
    """
    Входное состояние для агента.
    """

    host: str


class AgentOutputState(TypedDict):
    """
    Выходное состояние для агента.
    """

    result: AnalysisResult


class AgentState(AgentInputState, AgentOutputState):
    """
    Состояние агента.
    """

    messages: Annotated[list[AnyMessage], add_messages]
