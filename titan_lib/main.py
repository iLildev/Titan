import os
from titan.bot import Titan
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Payfix_406Bot")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "AjrPlusBot")

last_post: str | None = None

bot = Titan(TOKEN)


def user_mention(name: str, user_id: int) -> str:
    return f"[{name}](tg://user?id={user_id})"


@bot.message()
async def on_bot_added(ctx):
    msg = ctx.update.raw.get("message", {})
    new_members = msg.get("new_chat_members", [])

    if not new_members:
        return

    # هل البوت نفسه تم إضافته؟
    bot_added = any(
        m.get("username") == BOT_USERNAME for m in new_members
    )

    if not bot_added:
        return

    chat_id = ctx.chat_id
    if not chat_id:
        return

    # -------------------------
    # رسالة 1: رابط آخر منشور
    # -------------------------
    if last_post:
        await ctx.api.send_message(
            chat_id=chat_id,
            text=last_post
        )

    # -------------------------
    # هل تمت إضافته كمشرف؟
    # (نستخدم أول من أضافه كمرجع)
    # -------------------------
    adder = msg.get("from", {})
    adder_name = adder.get("first_name", "Unknown")
    adder_id = adder.get("id")

    is_admin_action = msg.get("new_chat_members")

    # Telegram لا يفرّق هنا بشكل مباشر بين عضو/مشرف في هذا الحدث
    # لذلك نعتمد على chat_member في حالات متقدمة (حالياً نبسطها)
    # ونفترض: إذا كان هناك from → نعرض رسالة التفعيل دائماً عند الإضافة

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "الاوامر",
                url=f"https://t.me/{BOT_USERNAME}?start=Commands"
            )
        ]
    ])

    # -------------------------
    # رسالة 2 (تفعيل + من أضاف البوت)
    # -------------------------
    await ctx.api.send_message(
        chat_id=chat_id,
        text=(
            f"⇜ من 「{user_mention(adder_name, adder_id)}」\n"
            f"⇜ تم تفعيل المجموعة تلقائياً\n"
            "༄"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


@bot.channel_post()
async def on_channel_post(ctx):
    global last_post
    post = ctx.update.channel_post
    if not post:
        return
    chat = post.get("chat", {})
    username = chat.get("username", "")
    message_id = post.get("message_id")
    if username and message_id:
        last_post = f"https://t.me/{username}/{message_id}"


bot.run(debug=True)