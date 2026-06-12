class Update:
    def __init__(self, raw: dict):
        self.raw = raw
        self.update_id = raw.get("update_id")
        self.message = raw.get("message")
        self.callback_query = raw.get("callback_query")

    def is_command(self) -> bool:
        if not self.message:
            return False
        text = self.message.get("text", "")
        return text.startswith("/")

    def get_command(self) -> str:
        if not self.is_command():
            return ""
        text = self.message.get("text", "")
        return text.split()[0][1:].split("@")[0].lower()

    def get_args(self) -> list:
        if not self.message:
            return []
        parts = self.message.get("text", "").split()
        return parts[1:] if len(parts) > 1 else []
