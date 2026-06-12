import aiohttp
from typing import Optional


class TelegramAPI:
    BASE_URL = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, token: str):
        self.token = token

    def _url(self, method: str) -> str:
        return self.BASE_URL.format(token=self.token, method=method)

    async def _request(self, method: str, payload: Optional[dict] = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(self._url(method), json=payload or {}) as resp:
                data = await resp.json()
                if not data.get("ok"):
                    raise RuntimeError(f"Telegram API error: {data.get('description')}")
                return data.get("result")

    async def get_updates(self, offset: int = 0, timeout: int = 10) -> list:
        result = await self._request("getUpdates", {"offset": offset, "timeout": timeout})
        return result or []

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML", **kwargs) -> dict:
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, **kwargs}
        return await self._request("sendMessage", payload)

    async def get_me(self) -> dict:
        return await self._request("getMe")
