"""
Промпты для агента
"""

SYSTEM_PROMPT = """You are a cyber security and Linux security expert."""

AGENT_PROMPT = """Analyze this host for security or network problems: {host}
Use any 1 tool of your choice to help you. First check if the host is reachable before using any other tool. Answer 'done' if you are finished."""

SUBSEQUENT_PROMPT = (
    """Use any 1 tool of your choice to help you. Answer 'done' if you are finished."""
)

ANALYSIS_PROMPT = """Analyze scan results for the host {host} and determine its network configuration, security details, and other useful information. Answer in Russian language."""
