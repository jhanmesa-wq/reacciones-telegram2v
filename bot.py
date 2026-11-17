import os
import random
import asyncio
import logging

from dotenv import load_dotenv
from telegram import Bot, Update, ReactionTypeEmoji
from telegram.constants import ChatType
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

# .env me: BOT_TOKENS=token1,token2,token3
# Pehla token main bot hai (updates receive karta hai),
# baaki bots sirf reaction lagate hain (unhe bhi group/channel me admin banao).
RAW_TOKENS = os.getenv("BOT_TOKENS") or os.getenv("BOT_TOKEN", "9116824186:AAEX-gtp7-3seRFQ6Iq7WtU69_gI-JfYdPc")
TOKENS = [t.strip() for t in RAW_TOKENS.split(",") if t.strip()]

# Telegram ke allowed reaction emojis (sirf yehi kaam karte hain)
REACTIONS = [
    "👍", "❤", "🔥", "🥰", "👏", "😁", "🤔", "🤯", "😱", "😢",
    "🎉", "🤩", "🙏", "👌", "🕊", "🤡", "🥱", "🥴", "😍", "🐳",
    "❤‍🔥", "🌚", "🌭", "💯", "🤣", "⚡", "🍌", "🏆", "💔", "🤨",
    "😐", "🍓", "🍾", "💋", "😈", "😴", "😭", "🤓", "👻", "👨‍💻",
    "👀", "🎃", "🙈", "😇", "😨", "🤝", "✍", "🤗", "🫡", "🎅",
    "🎄", "☃", "💅", "🤪", "🗿", "🆒", "💘", "🙉", "🦄", "😘",
    "💊", "🙊", "😎", "👾", "🤷", "😡",
]

DELAY = float(os.getenv("DELAY", "0.3"))  # bots ke beech delay (rate limit se bachne ko)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

extra_bots = []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "👋 Namaste! Main Reaction Bot hoon.\n\n"
        "Mujhe group/channel me admin bana do, "
        "main har message par alag alag emoji reaction lagaunga.\n\n"
        "👨‍💻 Developer: Aditya"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "📌 Commands:\n"
        "/start - Bot start karo\n"
        "/help - Madad\n\n"
        "Setup:\n"
        "1. Bot ko group/channel me admin banao\n"
        "2. BotFather → /setprivacy → Disable\n\n"
        "👨‍💻 Developer: Aditya"
    )


async def react_with(bot: Bot, chat_id: int, message_id: int, emoji: str):
    try:
        await bot.set_message_reaction(
            chat_id=chat_id,
            message_id=message_id,
            reaction=[ReactionTypeEmoji(emoji)],
        )
    except Exception as e:
        logger.warning("Reaction fail (%s): %s", emoji, e)


async def react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if msg is None or update.effective_chat.type == ChatType.PRIVATE:
        return

    chat_id, message_id = msg.chat_id, msg.message_id

    # Har bot ko alag emoji milega
    emojis = random.sample(REACTIONS, k=min(len(TOKENS), len(REACTIONS)))

    # Main bot
    await react_with(context.bot, chat_id, message_id, emojis[0])

    # Baaki bots
    for bot, emoji in zip(extra_bots, emojis[1:]):
        await asyncio.sleep(DELAY)
        await react_with(bot, chat_id, message_id, emoji)


def main():
    if not TOKENS:
        raise SystemExit("BOT_TOKENS set karo (.env file me, comma se alag karke).")

    app = Application.builder().token(TOKENS[0]).build()

    for t in TOKENS[1:]:
        extra_bots.append(Bot(t))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, react))

    logger.info("Bot chalu | Total bots: %d | Emojis: %d | Developer: Aditya",
                len(TOKENS), len(REACTIONS))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
