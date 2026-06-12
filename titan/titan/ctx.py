from .telegram import TelegramAPI


class Context:
    def __init__(self, update: dict, api: TelegramAPI):
        self._update = update
        self.api = api
        self.message = update.get("message", {})
        self.chat_id = self.message.get("chat", {}).get("id")
        self.user = self.message.get("from", {})
        self.text = self.message.get("text", "")

    async def reply(self, text: str, **kwargs):
        return await self.api.send_message(self.chat_id, text, **kwargs)

    async def send(self, chat_id: int, text: str, **kwargs):
        return await self.api.send_message(chat_id, text, **kwargs)
