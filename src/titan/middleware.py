from __future__ import annotations

from typing import Awaitable, Callable

from titan.ctx import Context


Middleware = Callable[[Context], Awaitable[bool | None]]


class MiddlewareChain:
    """
    سلسلة middleware اختيارية تُنفَّذ قبل كل handler.

    كل middleware تستلم ctx وتقرأ منه فقط.
    إذا أعادت False → يتوقف الـ update ولا يصل لأي handler.
    أي قيمة أخرى (True أو None) → يكمل الـ update مساره الطبيعي.

    لا يوجد أي logic أو queries داخل MiddlewareChain نفسها —
    فقط تنفيذ متسلسل للدوال المسجلة.
    """

    def __init__(self) -> None:
        self._chain: list[Middleware] = []

    def add(self, fn: Middleware) -> None:
        self._chain.append(fn)

    async def run(self, ctx: Context) -> bool:
        for fn in self._chain:
            result = await fn(ctx)
            if result is False:
                return False
        return True
