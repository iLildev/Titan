"""
titan.bot

هذا الملف هو المحرك الأساسي لـ Titan.

مسؤوليته:
- تشغيل البوت
- جلب التحديثات من Telegram
- تمريرها إلى Update ثم Context
- تنفيذ الـ handlers المسجلة

لا يحتوي على أي منطق خاص بالبوت نفسه.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable

from titan.telegram import Telegram
from titan.update import Update
from titan.ctx import Context


Handler = Callable[[Context], Any]


class Titan:
    """
    الكلاس الرئيسي الذي يستخدمه المطور.

    هذا هو Public API الخاص بـ Titan.
    """

    # -------------------------
    # Logging
    # -------------------------
    def log(self, msg: str) -> None:
        print(f"[Titan] {msg}")

    def __init__(self, token: str) -> None:
        self.api = Telegram(token)

        self.commands: dict[str, Handler] = {}
        self.messages: list[Handler] = []

        self.offset: int = 0

    # -------------------------
    # تسجيل الأوامر
    # -------------------------
    def command(self, name: str):
        def decorator(func: Handler):
            self.commands[name] = func
            return func
        return decorator

    # -------------------------
    # تسجيل الرسائل
    # -------------------------
    def message(self):
        def decorator(func: Handler):
            self.messages.append(func)
            return func
        return decorator

    # -------------------------
    # معالجة التحديث
    # -------------------------
    async def _handle_update(self, raw_update: dict[str, Any]) -> None:
        update = Update(raw_update)
        ctx = Context(update, self.api)

        text = update.text

        if text and text.startswith("/"):
            command = text.split()[0][1:]
            handler = self.commands.get(command)

            if handler:
                await handler(ctx)
                return

        for handler in self.messages:
            await handler(ctx)

    # -------------------------
    # التشغيل الأساسي
    # -------------------------
    async def run_async(self, debug: bool = False) -> None:
        await self.api.start()
        self.log("Bot started")

        try:
            while True:
                updates = await self.api.get_updates(
                    offset=self.offset + 1
                )

                for raw in updates:
                    self.offset = raw["update_id"]

                    if debug:
                        self.log(f"update received: {raw}")

                    await self._handle_update(raw)

                await asyncio.sleep(0.2)

        finally:
            self.log("Bot stopped")
            await self.api.close()

    # -------------------------
    # entry point
    # -------------------------
    def run(self, debug: bool = False) -> None:
        asyncio.run(self.run_async(debug=debug))