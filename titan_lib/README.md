# Titan

Titan is a simple and modern framework for building Telegram bots.

## Example

```python
from titan import Titan

bot = Titan("YOUR_TOKEN")

@bot.message()
async def handler(ctx):
    await ctx.reply("Hello World")

bot.run()