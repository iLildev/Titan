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
        self.messages: list[Handler] = []  
        self.channel_posts: list[Handler] = []  

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
    def command(self, name: str):  
        def decorator(func: Handler):  
            self.commands[name] = func  
            return func  
        return decorator  

    def message(self):  
        def decorator(func: Handler):  
            self.messages.append(func)  
            return func  
        return decorator  

    def channel_post(self):  
        def decorator(func: Handler):  
            self.channel_posts.append(func)  
            return func  
        return decorator  

    # -------------------------  
    # Update handling  
    # -------------------------  
    async def _handle_update(self, raw_update: dict[str, Any]) -> None:  
        update = Update(raw_update)  
        ctx = Context(update, self.api)  

        # channel post  
        if update.channel_post is not None:  
            for handler in self.channel_posts:  
                await handler(ctx)  
            return  

        # message / command  
        text = update.text  
        if text is None:  
            for handler in self.messages:  
                await handler(ctx)  
            return  

        command = self._extract_command(text)  
        if command is None:  
            for handler in self.messages:  
                await handler(ctx)  
            return  

        handler = self.commands.get(command)  
        if handler is not None:  
            await handler(ctx)  
            return  

        for handler in self.messages:  
            await handler(ctx)  

    # -------------------------  
    # Runtime  
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
    # Entry point  
    # -------------------------  
    def run(self, debug: bool = False) -> None:  
        asyncio.run(self.run_async(debug=debug))