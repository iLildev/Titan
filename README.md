# Titan

A simple and modern framework for building Telegram bots in Python.

Built around clean events, readable code, and a developer-friendly context system.

---

## Installation

```bash
pip install titanx
```

## Quick Start

```python
from titan import Titan

bot = Titan("YOUR_TOKEN")

@bot.on("message")
async def handler(ctx):
    await ctx.reply("Hello World")

bot.run()
```

## Events

```python
@bot.on("message")
async def handler(ctx):
    ...

@bot.on("callback")
async def handler(ctx):
    ...

@bot.on("channel")
async def handler(ctx):
    ...
```

## Commands

```python
@bot.command("start")
async def start(ctx):
    await ctx.reply("Welcome!")
```

## Context

Titan provides useful objects directly through `ctx`:

```python
@bot.on("message")
async def handler(ctx):
    print(ctx.sender.id)
    print(ctx.chat.id)
    print(ctx.text)

    await ctx.reply("Hello")
```

| Property | Description |
|---|---|
| `ctx.sender` | The user who sent the message |
| `ctx.chat` | The chat the message was sent in |
| `ctx.message` | The message object |
| `ctx.text` | The message text |

## Inline Keyboards

```python
from titan import Titan, InlineKeyboard, InlineButton

bot = Titan("YOUR_TOKEN")

@bot.on("message")
async def handler(ctx):
    keyboard = (
        InlineKeyboard()
        .row()
        .button(InlineButton("Click me", callback_data="clicked"))
    )
    await ctx.reply("Choose an option:", reply_markup=keyboard)

@bot.callback("clicked")
async def on_click(ctx):
    await ctx.answer_callback("You clicked it!")
```

## Middleware

```python
@bot.middleware
async def logger(ctx, next):
    print(f"Update from {ctx.user_id}")
    await next()
```

## Philosophy

Titan aims to make bot code describe what is happening instead of exposing Telegram API complexity.

- Simple things should be simple.
- Complex things should remain possible.

## License

MIT
