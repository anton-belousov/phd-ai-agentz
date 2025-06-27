"""
Утилиты для промптов
"""

from langchain_core.prompts import ChatPromptTemplate


def get_prompt_template(
    prompt: str, system_prompt: str | None = None
) -> ChatPromptTemplate:
    """
    Получает шаблон промпта
    """
    messages: list[tuple[str, str]] = []

    if system_prompt:
        messages.append(("system", system_prompt))

    messages.append(("user", prompt))

    return ChatPromptTemplate.from_messages(messages)
