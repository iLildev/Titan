"""
titan.ctx

يمثل Context الخاص بكل Update.

هذا الكائن هو ما يتعامل معه المطور داخل handlers.

هدفه:
- تبسيط الوصول لبيانات الرسالة
- توفير أدوات جاهزة (reply, ban, delete)
- إخفاء تفاصيل Telegram API بالكامل
"""

from __future__ import annotations

from typing import Any

from titan.telegram import Telegram
from titan.update import Update


class Context:
    """
    كائن السياق المستخدم داخل كل handler.

    يحتوي على:
    - البيانات المستخرجة من Update
    - أدوات للتفاعل مع Telegram
    """

    def __init__(self, update: Update, api: Telegram) -> None:
        self.update = update
        self.api = api

    # -------------------------
    # Helpers داخلية (مهمة)
    # -------------------------

    def _require_chat_id(self) -> int | None:
        return self.update.chat_id

    # -------------------------
    # بيانات الرسالة
    # -------------------------

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

    # -------------------------
    # أدوات التفاعل (Actions)
    # -------------------------

    async def reply(self, text: str) -> Any:
        """
        إرسال رسالة رد في نفس الشات.
        """

        chat_id = self._require_chat_id()

        if not chat_id:
            return None

        return await self.api.send_message(
            chat_id=chat_id,
            text=text,
        )

    async def delete_message(self) -> Any:
        
        """
        حذف الرسالة الحالية.
        """

        chat_id = self._require_chat_id()

        if not chat_id or self.update.message_id is None:
            return None

        return await self.api.delete_message(
            chat_id=chat_id,
            message_id=self.update.message_id,
        )

    async def ban_user(self, user_id: int | None = None) -> Any:
        """
        حظر مستخدم من الشات.

        إذا لم يتم تمرير user_id سيتم حظر صاحب الرسالة.
        """

        chat_id = self._require_chat_id()
        target_user = user_id or self.user_id

        if not chat_id or target_user is None:
            return None

        return await self.api.ban_user(
            chat_id=chat_id,
            user_id=target_user,
        )

    # -------------------------
    # أدوات مساعدة
    # -------------------------

    def is_group(self) -> bool:
        return self.update.chat_type in ("group", "supergroup")

    def is_private(self) -> bool:
        return self.update.chat_type == "private"