"""
titan.keyboard

أدوات بناء لوحات المفاتيح لـ Telegram.

الهدف:
- توفير واجهة بسيطة لبناء Inline keyboards
- إخفاء بنية JSON الخام من المطور
- لا يتطلب استيراد أي شيء من Telegram SDK خارجي
"""

from __future__ import annotations

from typing import Any


class InlineButton:
    """
    زر واحد داخل Inline keyboard.

    يدعم:
    - callback_data: لتشغيل @bot.on("callback")
    - url: لفتح رابط مباشرة
    """

    def __init__(
        self,
        text: str,
        *,
        callback_data: str | None = None,
        url: str | None = None,
    ) -> None:
        self.text = text
        self.callback_data = callback_data
        self.url = url

    # -------------------------
    # Export
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"text": self.text}

        if self.callback_data is not None:
            data["callback_data"] = self.callback_data

        if self.url is not None:
            data["url"] = self.url

        return data


class InlineKeyboard:
    """
    لوحة مفاتيح Inline قابلة للبناء بشكل سلسلة.

    مثال:
        kb = (
            InlineKeyboard()
            .add("✅ موافق", callback_data="yes")
            .add("❌ رفض", callback_data="no")
            .row()
            .add("🔗 رابط", url="https://example.com")
        )

        await ctx.reply("اختر:", reply_markup=kb)
    """

    def __init__(self) -> None:
        self._rows: list[list[InlineButton]] = [[]]

    # -------------------------
    # Building
    # -------------------------

    def add(
        self,
        text: str,
        *,
        callback_data: str | None = None,
        url: str | None = None,
    ) -> InlineKeyboard:
        """إضافة زر للصف الحالي."""

        button = InlineButton(text, callback_data=callback_data, url=url)
        self._rows[-1].append(button)
        return self

    def row(self) -> InlineKeyboard:
        """البدء بصف جديد."""

        self._rows.append([])
        return self

    # -------------------------
    # Export
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "inline_keyboard": [
                [btn.to_dict() for btn in row]
                for row in self._rows
                if row
            ]
        }
