import os
from titan import Titan

token = os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not token:
    print("[Titan] No TELEGRAM_BOT_TOKEN set. Set it in Secrets to run your bot.")
    print("[Titan] Example usage:")
    print("")
    print("  from titan import Titan")
    print("")
    print("  bot = Titan('YOUR_TOKEN')")
    print("")
    print("  @bot.on('message')")
    print("  async def handler(ctx):")
    print("      await ctx.reply('Hello World')")
    print("")
    print("  bot.run()")
else:
    bot = Titan(token)

    @bot.on("message")
    async def handler(ctx):
        await ctx.reply("Hello! I'm powered by Titan.")

    bot.run()
