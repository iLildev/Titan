import asyncio
from .telegram import TelegramAPI
from .handlers.commands import CommandHandler
from .handlers.messages import MessageHandler


class Bot:
    def __init__(self, token: str):
        self.token = token
        self.api = TelegramAPI(token)
        self.command_handler = CommandHandler()
        self.message_handler = MessageHandler()
        self._offset = 0

    def command(self, command: str):
        def decorator(func):
            self.command_handler.register(command, func)
            return func
        return decorator

    def message(self, filter_func=None):
        def decorator(func):
            self.message_handler.register(func, filter_func)
            return func
        return decorator

    async def process_update(self, update):
        from .update import Update
        u = Update(update)

        if u.is_command():
            await self.command_handler.handle(u)
        elif u.message:
            await self.message_handler.handle(u)

    async def _poll(self):
        while True:
            updates = await self.api.get_updates(self._offset)
            for raw in updates:
                self._offset = raw["update_id"] + 1
                await self.process_update(raw)
            await asyncio.sleep(0.5)

    def run(self):
        asyncio.run(self._poll())
