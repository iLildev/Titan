from titan import Bot
from titan.filters import contains

bot = Bot(token="YOUR_BOT_TOKEN_HERE")


@bot.command("start")
async def start(ctx):
    await ctx.reply("Hello! I'm powered by Titan 🤖\nSend me anything and I'll echo it back.")


@bot.command("help")
async def help_cmd(ctx):
    await ctx.reply(
        "<b>Available Commands</b>\n"
        "/start — Start the bot\n"
        "/help — Show this help message"
    )


@bot.message(contains("hello"))
async def greet(ctx):
    name = ctx.user.get("first_name", "there")
    await ctx.reply(f"Hey {name}! 👋")


@bot.message()
async def echo(ctx):
    if ctx.text:
        await ctx.reply(f"You said: {ctx.text}")


if __name__ == "__main__":
    bot.run()
