"""
Agent data models
"""

from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class AnalysisResult(BaseModel):
    """
    Result of the security scan.
    """

    has_security_issues: bool = Field(
        description="Whether the host has security issues"
    )
    identified_issues: list[str] = Field(
        description="A list of identified security issues"
    )
    ports: list[str] = Field(description="A list of open ports on the host")
    services: list[str] = Field(description="A list of services running on the host")
    network_info: str = Field(
        description="The network information of the host - IP address, ping, traceroute, etc."
    )
    os_info: str = Field(description="The operating system information of the host")
    other_information: str = Field(description="Other information about the host")


class AgentInputState(TypedDict):
    """
    Input state for the agent.
    """

    host: str


class AgentOutputState(TypedDict):
    """
    Output state for the agent.
    """

    result: AnalysisResult


class AgentState(AgentInputState, AgentOutputState):
    """
    State of the agent.
    """

    messages: Annotated[list[AnyMessage], add_messages]
