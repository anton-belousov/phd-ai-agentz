"""
Обработчик Langfuse
"""

from langfuse.langchain import CallbackHandler

_langfuse_handler: CallbackHandler | None = None


def get_callback_handler() -> CallbackHandler:
    """
    Получение обработчика Langfuse
    """
    global _langfuse_handler

    if _langfuse_handler is None:
        _langfuse_handler = CallbackHandler()

    return _langfuse_handler
