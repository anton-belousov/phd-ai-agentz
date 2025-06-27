"""
Agent data models
"""

from typing import Any

from langgraph_swarm import SwarmState
from pydantic import BaseModel, Field


class CustomSwarmState(SwarmState):
    """
    Custom swarm state.
    """

    structured_response: Any


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
    web_apps: list[str] = Field(
        description="Список веб-приложений, запущенных на хосте"
    )
    other_information: str = Field(description="Другая информация о хосте")
