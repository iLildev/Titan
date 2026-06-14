from __future__ import annotations

import asyncio
from typing import Any, Callable

from titan.telegram import Telegram
from titan.update import Update
from titan.ctx import Context


Handler = Callable[[Context], Any]


class Titan:
    def __init__(self, token: str) -> None:
        self.api = Telegram(token)
        self.commands: dict[str, Handler] = {}
        self.messages: list[Handler] = []
        self.channel_posts: list[Handler] = []
        self._offset: int = 0

    def log(self, text: str) -> None:
        print(f"[Titan] {text}")

    def command(self, name: str):
        def decorator(func: Handler):
            self.commands[name] = func
            return func
        return decorator

    def message(self):
        def decorator(func: Handler):
            self.messages.append(func)
            return func
        return decorator

    def channel_post(self):
        def decorator(func: Handler):
            self.channel_posts.append(func)
            return func
        return decorator

    async def _dispatch(self, raw: dict[str, Any]) -> None:
        update = Update(raw)
        ctx = Context(update, self.api)

        if update.is_channel_post():
            for handler in self.channel_posts:
                await handler(ctx)
            return

        if update.text and update.text.startswith("/"):
            command_name = update.text.split()[0][1:]
            handler = self.commands.get(command_name)
            if handler:
                await handler(ctx)
                return

        for handler in self.messages:
            await handler(ctx)

    async def _poll(self, debug: bool = False) -> None:
        await self.api.open_session()
        self.log("Bot started")
        try:
            while True:
                updates = await self.api.get_updates(offset=self._offset + 1)
                for raw in updates:
                    self._offset = raw["update_id"]
                    if debug:
                        self.log(f"update received: {raw}")
                    await self._dispatch(raw)
                await asyncio.sleep(0.2)
        finally:
            self.log("Bot stopped")
            await self.api.close_session()

    def run(self, debug: bool = False) -> None:
        asyncio.run(self._poll(debug=debug))
