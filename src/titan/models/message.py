"""
models.message

تمثيل مبسط لرسالة Telegram.

هذا الكائن يوفر واجهة سهلة للتعامل مع بيانات الرسالة
بدلاً من الوصول المباشر إلى JSON القادم من Telegram.
"""

from __future__ import annotations

from typing import Any

from titan.telegram import Telegram


class Message:
    """
    تمثيل مبسط لرسالة Telegram.

    الهدف:
    جمع بيانات الرسالة وتوفير أدوات أساسية للتعامل معها.
    """

    def __init__(self, raw: dict[str, Any] | None, api: Telegram | None = None) -> None:
        self.raw = raw or {}
        self.api = api

    # -------------------------
    # Message data
    # -------------------------

    @property
    def id(self) -> int | None:
        return self.raw.get("message_id")

    @property
    def text(self) -> str | None:
        return self.raw.get("text")

    # -------------------------
    # Chat data (optional shortcut)
    # -------------------------

    @property
    def chat_id(self) -> int | None:
        chat = self.raw.get("chat")
        return chat.get("id") if chat else None

    # -------------------------
    # Actions
    # -------------------------

    async def reply(self, text: str) -> Any:
        """
        الرد على نفس الرسالة.
        """

        if self.api is None:
            return None

        chat_id = self.chat_id
        if chat_id is None:
            return None

        return await self.api.send_message(
            chat_id=chat_id,
            text=text,
        )

    async def delete(self) -> Any:
        """
        حذف الرسالة.
        """

        if self.api is None:
            return None

        chat_id = self.chat_id
        message_id = self.id

        if chat_id is None or message_id is None:
            return None

        return await self.api.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )

    # -------------------------
    # Export
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        return self.raw