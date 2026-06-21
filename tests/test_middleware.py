import pytest
from unittest.mock import AsyncMock, MagicMock
from titan.bot import Titan
from titan.ctx import Context
from titan.update import Update
from titan.middleware import MiddlewareChain


def make_bot():
    bot = Titan("fake-token")
    bot.api = MagicMock()
    bot.api.send_message = AsyncMock(return_value={"ok": True})
    return bot


RAW_MESSAGE = {
    "update_id": 1,
    "message": {
        "message_id": 10,
        "text": "hello",
        "from": {"id": 99, "username": "ali"},
        "chat": {"id": 200, "type": "private"},
    },
}

RAW_MESSAGE_USER_2 = {
    "update_id": 2,
    "message": {
        "message_id": 11,
        "text": "hi",
        "from": {"id": 55, "username": "bob"},
        "chat": {"id": 200, "type": "private"},
    },
}

RAW_NO_USER = {
    "update_id": 3,
    "message": {
        "message_id": 12,
        "chat": {"id": 300, "type": "channel"},
    },
}


class TestContextIsBanned:
    def test_is_banned_default_false(self):
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        assert ctx.is_banned is False

    def test_is_banned_is_bool(self):
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        assert isinstance(ctx.is_banned, bool)


class TestBotBannedUsers:
    def test_banned_users_initially_empty(self):
        bot = make_bot()
        assert bot.banned_users == set()

    def test_add_to_banned_users(self):
        bot = make_bot()
        bot.banned_users.add(99)
        assert 99 in bot.banned_users

    def test_remove_from_banned_users(self):
        bot = make_bot()
        bot.banned_users.add(99)
        bot.banned_users.discard(99)
        assert 99 not in bot.banned_users

    @pytest.mark.asyncio
    async def test_ctx_is_banned_true_for_banned_user(self):
        bot = make_bot()
        bot.banned_users.add(99)
        received = []

        @bot.on("message")
        async def handler(ctx):
            received.append(ctx.is_banned)

        await bot._handle_update(RAW_MESSAGE)
        assert received == [True]

    @pytest.mark.asyncio
    async def test_ctx_is_banned_false_for_non_banned_user(self):
        bot = make_bot()
        received = []

        @bot.on("message")
        async def handler(ctx):
            received.append(ctx.is_banned)

        await bot._handle_update(RAW_MESSAGE)
        assert received == [False]

    @pytest.mark.asyncio
    async def test_ctx_is_banned_false_when_no_user_id(self):
        bot = make_bot()
        bot.banned_users.add(99)
        received = []

        @bot.on("message")
        async def handler(ctx):
            received.append(ctx.is_banned)

        await bot._handle_update(RAW_NO_USER)
        assert received == [False]

    @pytest.mark.asyncio
    async def test_only_banned_user_is_marked(self):
        bot = make_bot()
        bot.banned_users.add(99)
        received = {}

        @bot.on("message")
        async def handler(ctx):
            received[ctx.user_id] = ctx.is_banned

        await bot._handle_update(RAW_MESSAGE)
        await bot._handle_update(RAW_MESSAGE_USER_2)
        assert received[99] is True
        assert received[55] is False


class TestMiddlewareChain:
    @pytest.mark.asyncio
    async def test_empty_chain_returns_true(self):
        chain = MiddlewareChain()
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        result = await chain.run(ctx)
        assert result is True

    @pytest.mark.asyncio
    async def test_middleware_returning_true_continues(self):
        chain = MiddlewareChain()

        async def allow(ctx):
            return True

        chain.add(allow)
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        result = await chain.run(ctx)
        assert result is True

    @pytest.mark.asyncio
    async def test_middleware_returning_none_continues(self):
        chain = MiddlewareChain()

        async def passthrough(ctx):
            return None

        chain.add(passthrough)
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        result = await chain.run(ctx)
        assert result is True

    @pytest.mark.asyncio
    async def test_middleware_returning_false_stops(self):
        chain = MiddlewareChain()

        async def block(ctx):
            return False

        chain.add(block)
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        result = await chain.run(ctx)
        assert result is False

    @pytest.mark.asyncio
    async def test_false_stops_remaining_middleware(self):
        chain = MiddlewareChain()
        executed = []

        async def first(ctx):
            executed.append("first")
            return False

        async def second(ctx):
            executed.append("second")

        chain.add(first)
        chain.add(second)
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        await chain.run(ctx)
        assert executed == ["first"]

    @pytest.mark.asyncio
    async def test_multiple_middleware_all_pass(self):
        chain = MiddlewareChain()
        executed = []

        async def m1(ctx):
            executed.append(1)

        async def m2(ctx):
            executed.append(2)

        chain.add(m1)
        chain.add(m2)
        api = MagicMock()
        ctx = Context(Update(RAW_MESSAGE), api)
        result = await chain.run(ctx)
        assert result is True
        assert executed == [1, 2]


class TestBotUse:
    def test_use_registers_middleware(self):
        bot = make_bot()

        async def mw(ctx): pass

        bot.use(mw)
        assert mw in bot.middleware_chain._chain

    def test_use_returns_fn(self):
        bot = make_bot()

        async def mw(ctx): pass

        result = bot.use(mw)
        assert result is mw

    def test_use_as_decorator(self):
        bot = make_bot()

        @bot.use
        async def mw(ctx): pass

        assert mw in bot.middleware_chain._chain

    @pytest.mark.asyncio
    async def test_middleware_blocks_handler(self):
        bot = make_bot()
        bot.banned_users.add(99)
        called = []

        @bot.use
        async def check_banned(ctx):
            if ctx.is_banned:
                return False

        @bot.on("message")
        async def handler(ctx):
            called.append(True)

        await bot._handle_update(RAW_MESSAGE)
        assert called == []

    @pytest.mark.asyncio
    async def test_middleware_allows_non_banned(self):
        bot = make_bot()
        called = []

        @bot.use
        async def check_banned(ctx):
            if ctx.is_banned:
                return False

        @bot.on("message")
        async def handler(ctx):
            called.append(True)

        await bot._handle_update(RAW_MESSAGE)
        assert called == [True]

    @pytest.mark.asyncio
    async def test_no_middleware_registered_update_passes(self):
        bot = make_bot()
        called = []

        @bot.on("message")
        async def handler(ctx):
            called.append(True)

        await bot._handle_update(RAW_MESSAGE)
        assert called == [True]
