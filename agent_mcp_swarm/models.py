"""
Модели данных для агента
"""

from typing import Any

from langgraph_swarm import SwarmState
from pydantic import BaseModel, Field


class CustomSwarmState(SwarmState):
    """
    Выходное состояние для роя
    """

    structured_response: Any


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


class ScanTaskStatus(BaseModel):
    """
    Статус задачи сканирования.
    """

    run_id: str = Field(description="Идентификатор задачи")
    status: str = Field(description="Статус задачи")
    result: AnalysisResult | str | None = Field(description="Результат сканирования")
