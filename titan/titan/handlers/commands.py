from typing import Callable


class CommandHandler:
    def __init__(self):
        self._handlers: dict[str, Callable] = {}

    def register(self, command: str, func: Callable):
        self._handlers[command.lower()] = func

    async def handle(self, update):
        from ..ctx import Context
        command = update.get_command()
        func = self._handlers.get(command)
        if func:
            ctx = Context(update.raw, None)
            await func(ctx)
