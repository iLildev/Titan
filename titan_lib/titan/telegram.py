from __future__ import annotations

from typing import Any

import aiohttp


class TelegramError(Exception):
    pass


class Telegram:
    def __init__(self, token: str) -> None:
        self.token = token
        self._base_url = f"https://api.telegram.org/bot{token}"
        self._session: aiohttp.ClientSession | None = None

    async def open_session(self) -> None:
        if self._session is None:
            self._session = aiohttp.ClientSession()

    async def close_session(self) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def _call(self, method: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._session is None:
            raise TelegramError("Session is not open. Call open_session() first.")

        url = f"{self._base_url}/{method}"

        async with self._session.post(url, json=payload or {}) as response:
            result: dict[str, Any] = await response.json()

        if not result.get("ok"):
            raise TelegramError(result.get("description", "Unknown Telegram error."))

        return result

    async def get_updates(self, offset: int = 0, timeout: int = 30) -> list[dict[str, Any]]:
        result = await self._call("getUpdates", {"offset": offset, "timeout": timeout})
        return result["result"]

    async def send_message(
        self,
        chat_id: int,
        text: str,
        parse_mode: str | None = None,
        reply_markup: Any | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup is not None:
            payload["reply_markup"] = (
                reply_markup.to_dict() if hasattr(reply_markup, "to_dict") else reply_markup
            )
        return await self._call("sendMessage", payload)

    async def delete_message(self, chat_id: int, message_id: int) -> dict[str, Any]:
        return await self._call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def ban_user(self, chat_id: int, user_id: int) -> dict[str, Any]:
        return await self._call("banChatMember", {"chat_id": chat_id, "user_id": user_id})
