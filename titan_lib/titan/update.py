"""
titan.update

تحويل بيانات Telegram Update الخام إلى شكل مبسط
يمكن لبقية Titan استخدامه بسهولة.

هذا الملف لا يحتوي على أي منطق للبوت.
فقط استخراج بيانات.
"""

from __future__ import annotations

from typing import Any


class Update:
    """
    تمثيل مبسط لرسالة Telegram Update.

    الهدف:
    إزالة التعقيد من بنية JSON القادمة من Telegram
    وتحويلها إلى واجهة واضحة وسهلة الاستخدام.
    """

    def __init__(self, raw: dict[str, Any]) -> None:
        self.raw = raw
        self.message = raw.get("message")
        self.channel_post = raw.get("channel_post")
        self.callback_query = raw.get("callback_query")

    # -------------------------
    # Helpers داخلية
    # -------------------------

    def _msg(self):
        """
        إرجاع الكائن الأساسي للتحديث.

        يدعم:
        - message
        - channel_post

        ويمكن توسيعه مستقبلاً لأنواع أخرى.
        """
        return self.message or self.channel_post

    def _chat(self):
        msg = self._msg()
        if not msg:
            return None
        return msg.get("chat")

    def _user(self):
        msg = self._msg()
        if not msg:
            return None
        return msg.get("from")

    # -------------------------
    # معلومات الرسالة
    # -------------------------

    @property
    def text(self) -> str | None:
        msg = self._msg()
        return msg.get("text") if msg else None

    @property
    def message_id(self) -> int | None:
        msg = self._msg()
        return msg.get("message_id") if msg else None

    # -------------------------
    # معلومات المستخدم
    # -------------------------

    @property
    def user_id(self) -> int | None:
        user = self._user()
        return user.get("id") if user else None

    @property
    def username(self) -> str | None:
        user = self._user()
        return user.get("username") if user else None

    # -------------------------
    # معلومات الشات
    # -------------------------

    @property
    def chat_id(self) -> int | None:
        chat = self._chat()
        return chat.get("id") if chat else None

    @property
    def chat_type(self) -> str | None:
        chat = self._chat()
        return chat.get("type") if chat else None

    # -------------------------
    # أدوات مساعدة
    # -------------------------

    def is_message(self) -> bool:
        return self.message is not None

    def is_channel_post(self) -> bool:
        return self.channel_post is not None

    def has_text(self) -> bool:
        return self.text is not None

    # -------------------------
    # تصدير داخلي
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        return self.raw