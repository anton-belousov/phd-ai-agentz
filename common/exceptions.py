from rich.console import Console
from rich.panel import Panel

console = Console()


def print_exception(e: Exception):
    """
    Выводит ошибку в консоль
    """
    if isinstance(e, ExceptionGroup):
        for exc in e.exceptions:
            print_exception(exc)
    else:
        console.print(Panel(str(e), title="Ошибка", border_style="red"))
