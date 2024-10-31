from telegram import Bot
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


bot = Bot(token=TELEGRAM_BOT_TOKEN)


async def send_message(text, chat_id):
    async with bot:
        await bot.send_message(text=text, chat_id=chat_id)


def notify_borrowing(book, user):
    message = f"Book {book.title} was borrowed by visitor with ID: {user.id}"

    asyncio.run(send_message(message, CHAT_ID))

