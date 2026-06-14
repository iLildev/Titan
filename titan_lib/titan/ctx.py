from __future__ import annotations

from typing import Any

from titan.telegram import Telegram
from titan.update import Update


class Context:
    def __init__(self, update: Update, api: Telegram) -> None:
        self.update = update
        self.api = api

    @property
    def text(self) -> str | None:
        return self.update.text

    @property
    def user_id(self) -> int | None:
        return self.update.user_id

    @property
    def chat_id(self) -> int | None:
        return self.update.chat_id

    @property
    def username(self) -> str | None:
        return self.update.username

    def is_group(self) -> bool:
        return self.update.chat_type in ("group", "supergroup")

    def is_private(self) -> bool:
        return self.update.chat_type == "private"

    async def reply(self, text: str, **kwargs) -> Any:
        if not self.update.chat_id:
            return None
        return await self.api.send_message(chat_id=self.update.chat_id, text=text, **kwargs)

    async def delete_message(self) -> Any:
        if not self.update.chat_id or self.update.message_id is None:
            return None
        return await self.api.delete_message(
            chat_id=self.update.chat_id,
            message_id=self.update.message_id,
        )

    async def ban_user(self, user_id: int | None = None) -> Any:
        target = user_id or self.update.user_id
        if not self.update.chat_id or target is None:
            return None
        return await self.api.ban_user(chat_id=self.update.chat_id, user_id=target)
