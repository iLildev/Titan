from __future__ import annotations

from typing import Any


class Update:
    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.message = raw.get("message")
        self.channel_post = raw.get("channel_post")
        self.callback_query = raw.get("callback_query")

    def _content(self) -> dict | None:
        return self.message or self.channel_post

    def _chat(self) -> dict | None:
        content = self._content()
        return content.get("chat") if content else None

    def _sender(self) -> dict | None:
        content = self._content()
        return content.get("from") if content else None

    @property
    def text(self) -> str | None:
        content = self._content()
        return content.get("text") if content else None

    @property
    def message_id(self) -> int | None:
        content = self._content()
        return content.get("message_id") if content else None

    @property
    def user_id(self) -> int | None:
        sender = self._sender()
        return sender.get("id") if sender else None

    @property
    def username(self) -> str | None:
        sender = self._sender()
        return sender.get("username") if sender else None

    @property
    def chat_id(self) -> int | None:
        chat = self._chat()
        return chat.get("id") if chat else None

    @property
    def chat_type(self) -> str | None:
        chat = self._chat()
        return chat.get("type") if chat else None

    def is_message(self) -> bool:
        return self.message is not None

    def is_channel_post(self) -> bool:
        return self.channel_post is not None

    def has_text(self) -> bool:
        return self.text is not None
