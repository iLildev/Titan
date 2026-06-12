# Titan

A lightweight, async Python framework for building Telegram bots.

## Features

- Async-first using `asyncio` and `aiohttp`
- Decorator-based command and message handlers
- Composable text filters
- Clean context object for replying and sending messages

## Installation

```bash
pip install aiohttp
```

Clone the repo and add `titan/` to your project, or install locally:

```bash
pip install -e .
```

## Quick Start

```python
from titan import Bot

bot = Bot(token="YOUR_BOT_TOKEN")

@bot.command("start")
async def start(ctx):
    await ctx.reply("Hello from Titan!")

bot.run()
```

## Project Structure

```
titan/
├── titan/
│   ├── bot.py          # Bot class — entry point, handler registration, polling loop
│   ├── ctx.py          # Context object passed to every handler
│   ├── update.py       # Update wrapper with helpers (is_command, get_args, etc.)
│   ├── telegram.py     # Raw Telegram Bot API client (aiohttp)
│   ├── handlers/
│   │   ├── commands.py # Routes /commands to registered handlers
│   │   └── messages.py # Routes plain messages through optional filters
│   └── filters/
│       └── text.py     # Built-in text filters (text, contains, startswith, regex)
├── examples/
│   └── hello.py        # Full working example bot
└── README.md
```

## Handlers

### Command handler

```python
@bot.command("start")
async def start(ctx):
    await ctx.reply("Started!")
```

### Message handler (no filter — catches all messages)

```python
@bot.message()
async def echo(ctx):
    await ctx.reply(ctx.text)
```

### Message handler with filter

```python
from titan.filters import contains

@bot.message(contains("hello"))
async def greet(ctx):
    await ctx.reply("Hey there!")
```

## Filters

| Filter | Description |
|---|---|
| `text("exact")` | Matches exact message text |
| `contains("word")` | Message contains the substring |
| `startswith("!")` | Message starts with a prefix |
| `regex(r"\d+")` | Message matches a regex pattern |

## Context (`ctx`)

| Attribute / Method | Description |
|---|---|
| `ctx.text` | The message text |
| `ctx.chat_id` | Chat ID of the incoming message |
| `ctx.user` | Sender info dict (`first_name`, `id`, etc.) |
| `ctx.reply(text)` | Reply to the current chat |
| `ctx.send(chat_id, text)` | Send a message to any chat |

## License

MIT
