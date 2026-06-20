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
from typing import Any, Callable, Awaitable  

from titan.telegram import Telegram  
from titan.update import Update  
from titan.ctx import Context  


Handler = Callable[[Context], Awaitable[Any]]  


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
        - "channel_post"  
        - "callback"  
        - أي حدث مستقبلي  
        """  

        def decorator(func: Handler):  
            self.handlers.setdefault(event, []).append(func)  
            return func  
        return decorator  

    def command(self, name: str):  
        """تسجيل أمر محدد مثل /start أو /help."""  

        def decorator(func: Handler):  
            self.commands[name] = func  
            return func  
        return decorator  

    # -------------------------  
    # Dispatch  
    # -------------------------  
    async def _dispatch(self, event: str, ctx: Context) -> None:  
        """تشغيل جميع الـ handlers المسجلة لحدث معين."""  

        for handler in self.handlers.get(event, []):  
            await handler(ctx)  

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

        # callback_query  
        if update.callback_query is not None:  
            await self._dispatch("callback", ctx)  
            return  

        # message / command  
        text = update.text  
        command = self._extract_command(text) if text else None  

        if command is not None:  
            handler = self.commands.get(command)  
            if handler is not None:  
                await handler(ctx)  
                return  

        await self._dispatch("message", ctx)  

    # -------------------------  
    # Runtime  
    # -------------------------  
    async def run_async(self, debug: bool = False) -> None:  
        await self.api.start()  
        self.log("Bot started")  

        # warm-up اختياري: تحميل معلومات البوت مسبقاً لتسريع أول استخدام  
        try:  
            me = await self.api.get_me()  
            username = me.get("username", "unknown")  
            self.log(f"Running as @{username}")  
        except Exception:  
            pass  

        try:  
            while True:  
                try:  
                    updates = await self.api.get_updates(  
                        offset=self.offset + 1  
                    )  

                    for raw in updates:  
                        self.offset = raw["update_id"]  

                        if debug:  
                            self.log(f"update received: {raw}")  

                        await self._handle_update(raw)  

                except Exception as e:  
                    self.log(f"Polling error: {e}")  

                # no sleep needed (long polling handles waiting)  

        finally:  
            self.log("Bot stopped")  
            await self.api.close()  

    # -------------------------  
    # Entry point  
    # -------------------------  
    def run(self, debug: bool = False) -> None:  
        asyncio.run(self.run_async(debug=debug))  
