"""
titan.bot

المحرك الأساسي لـ Titan.

مسؤوليته:
- تشغيل البوت
- جلب التحديثات من Telegram
- تمريرها إلى Update ثم Context
- تنفيذ الـ handlers المسجلة

لا يحتوي على أي منطق خاص بالبوت نفسه.
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Awaitable

from titan.errors import TitanError
from titan.telegram import Telegram
from titan.update import Update
from titan.ctx import Context


Handler = Callable[[Context], Awaitable[Any]]

_BACKOFF_BASE: float = 1.0
_BACKOFF_MAX: float = 30.0


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
        self.handlers: dict[str, list[Handler]] = {}
        self.callback_handlers: dict[str, Handler] = {}

        self.offset: int = 0

    # -------------------------
    # Utilities
    # -------------------------
    def _extract_command(self, text: str) -> str | None:
        """
        استخراج اسم الأمر من النص.

        يدعم:
        - /start
        - /start@BotName
        """

        if not text.startswith("/"):
            return None

        command = text.split(maxsplit=1)[0][1:]
        if not command:
            return None

        return command.split("@", 1)[0]

    # -------------------------
    # Registration
    # -------------------------
    def on(self, event: str):
        """
        تسجيل handler لحدث معين.

        يدعم أي اسم حدث:
        - "message"
        - "channel"
        - "callback"
        - "new_member"
        - "left_member"
        """

        def decorator(func: Handler):
            self.handlers.setdefault(event, []).append(func)
            return func
        return decorator

    def command(self, name: str):
        """
        تسجيل أمر محدد مثل /start أو /help.

        يرمي TitanError إذا كان الأمر مسجلاً مسبقاً.
        """

        def decorator(func: Handler):
            if name in self.commands:
                raise TitanError(
                    f"Command '{name}' is already registered. "
                    f"Each command can only have one handler."
                )
            self.commands[name] = func
            return func
        return decorator

    def callback(self, data: str):
        """
        تسجيل handler لزر callback محدد بناءً على callback_data.

        يرمي TitanError إذا كانت الـ data مسجلة مسبقاً.

        مثال:
            @bot.callback("yes")
            async def on_yes(ctx):
                await ctx.answer_callback()
                await ctx.reply("اخترت نعم")

        إذا لم يوجد handler مطابق لـ data، يُرسل الـ update
        إلى on("callback") إن وجد.
        """

        def decorator(func: Handler):
            if data in self.callback_handlers:
                raise TitanError(
                    f"Callback handler for '{data}' is already registered. "
                    f"Each callback_data value can only have one handler."
                )
            self.callback_handlers[data] = func
            return func
        return decorator

    # -------------------------
    # Dispatch
    # -------------------------
    async def _dispatch(self, event: str, ctx: Context) -> None:
        """تشغيل جميع الـ handlers المسجلة لحدث معين."""

        for handler in self.handlers.get(event, []):
            try:
                await handler(ctx)
            except Exception as e:
                self.log(f"Handler error [{event}]: {e}")

    # -------------------------
    # Update handling
    # -------------------------
    async def _handle_update(self, raw_update: dict[str, Any]) -> None:
        update = Update(raw_update)
        ctx = Context(update, self.api)

        # channel
        if update.channel_post is not None:
            await self._dispatch("channel", ctx)
            return

        # callback_query — route by data first, fallback to on("callback")
        if update.callback_query is not None:
            data = ctx.callback_data
            specific = self.callback_handlers.get(data) if data else None
            if specific is not None:
                try:
                    await specific(ctx)
                except Exception as e:
                    self.log(f"Callback handler error [{data}]: {e}")
            else:
                await self._dispatch("callback", ctx)
            return

        # semantic event aliases — قبل dispatch الرسائل العامة
        raw_msg = update._message()
        if raw_msg:
            if raw_msg.get("new_chat_members"):
                await self._dispatch("new_member", ctx)
                return
            if raw_msg.get("left_chat_member"):
                await self._dispatch("left_member", ctx)
                return

        # message / command
        text = update.text
        command = self._extract_command(text) if text else None

        if command is not None:
            handler = self.commands.get(command)
            if handler is not None:
                try:
                    await handler(ctx)
                except Exception as e:
                    self.log(f"Command handler error [{command}]: {e}")
                return

        await self._dispatch("message", ctx)

    # -------------------------
    # Runtime
    # -------------------------
    async def run_async(self, debug: bool = False) -> None:
        await self.api.start()
        self.log("Bot started")

        try:
            me = await self.api.get_me()
            username = me.get("username", "unknown")
            self.log(f"Running as @{username}")
        except Exception:
            pass

        backoff: float = 0.0

        try:
            while True:
                try:
                    updates = await self.api.get_updates(
                        offset=self.offset + 1
                    )

                    backoff = 0.0

                    for raw in updates:
                        self.offset = raw["update_id"]

                        if debug:
                            self.log(f"update received: {raw}")

                        await self._handle_update(raw)

                except Exception as e:
                    backoff = min(
                        backoff * 2 if backoff else _BACKOFF_BASE,
                        _BACKOFF_MAX,
                    )
                    self.log(f"Polling error: {e}. Retrying in {backoff:.0f}s...")
                    await asyncio.sleep(backoff)

        finally:
            self.log("Bot stopped")
            await self.api.close()

    # -------------------------
    # Entry point
    # -------------------------
    def run(self, debug: bool = False) -> None:
        asyncio.run(self.run_async(debug=debug))
