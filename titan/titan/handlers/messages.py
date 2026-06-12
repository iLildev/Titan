from typing import Callable, Optional


class MessageHandler:
    def __init__(self):
        self._handlers: list[tuple[Callable, Optional[Callable]]] = []

    def register(self, func: Callable, filter_func: Optional[Callable] = None):
        self._handlers.append((func, filter_func))

    async def handle(self, update):
        from ..ctx import Context
        ctx = Context(update.raw, None)
        for func, filter_func in self._handlers:
            if filter_func is None or filter_func(update):
                await func(ctx)
