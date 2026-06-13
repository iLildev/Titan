"""
التعامل المباشر مع Telegram Bot API.

جميع الطلبات إلى Telegram تمر من هذا الملف.
لا يحتوي على أوامر أو فلاتر أو منطق البوت.
"""

from __future__ import annotations

from typing import Any

import aiohttp


class TelegramError(Exception):
    """خطأ صادر من Telegram API."""
    pass


class Telegram:
    """واجهة بسيطة للتعامل مع Telegram Bot API."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

        # نعيد استخدام جلسة واحدة طوال عمر البوت
        # لتحسين الأداء وتقليل عدد الاتصالات.
        self.session: aiohttp.ClientSession | None = None

    async def start(self) -> None:
        """إنشاء جلسة HTTP إذا لم تكن موجودة."""

        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """إغلاق الجلسة عند إيقاف البوت."""

        if self.session is not None:
            await self.session.close()
            self.session = None

    async def request(
        self,
        method: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        إرسال طلب إلى Telegram API.
        """

        if self.session is None:
            raise TelegramError("Telegram session is not started.")

        url = f"{self.base_url}/{method}"

        async with self.session.post(url, json=data or {}) as response:
            result: dict[str, Any] = await response.json()

            if not result.get("ok"):
                raise TelegramError(
                    result.get("description", "Unknown Telegram error.")
                )

            return result

    async def get_updates(
        self,
        offset: int = 0,
        timeout: int = 30,
    ) -> list[dict[str, Any]]:
        """
        جلب التحديثات الجديدة باستخدام Long Polling.
        """

        result = await self.request(
            "getUpdates",
            {
                "offset": offset,
                "timeout": timeout,
            },
        )

        return result["result"]

    async def send_message(
        self,
        chat_id: int,
        text: str,
    ) -> dict[str, Any]:
        """إرسال رسالة نصية."""

        return await self.request(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": text,
            },
        )

    async def delete_message(
        self,
        chat_id: int,
        message_id: int,
    ) -> dict[str, Any]:
        """حذف رسالة."""

        return await self.request(
            "deleteMessage",
            {
                "chat_id": chat_id,
                "message_id": message_id,
            },
        )

    async def ban_user(
        self,
        chat_id: int,
        user_id: int,
    ) -> dict[str, Any]:
        """حظر مستخدم."""

        return await self.request(
            "banChatMember",
            {
                "chat_id": chat_id,
                "user_id": user_id,
            },
        )