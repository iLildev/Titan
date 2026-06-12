from typing import Callable


def text(value: str) -> Callable:
    def filter_func(update) -> bool:
        msg = update.message or {}
        return msg.get("text", "") == value
    return filter_func


def contains(value: str) -> Callable:
    def filter_func(update) -> bool:
        msg = update.message or {}
        return value in msg.get("text", "")
    return filter_func


def startswith(value: str) -> Callable:
    def filter_func(update) -> bool:
        msg = update.message or {}
        return msg.get("text", "").startswith(value)
    return filter_func


def regex(pattern: str) -> Callable:
    import re
    compiled = re.compile(pattern)

    def filter_func(update) -> bool:
        msg = update.message or {}
        return bool(compiled.search(msg.get("text", "")))
    return filter_func
