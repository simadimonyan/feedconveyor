import asyncio
import logging
import sys
import json

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.filters import Command

from handlers import habrparser

def load_data_from_json():
    try:
        with open('./configs/bot-config.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}
    
config = load_data_from_json()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = config["telegram"]["API_TOKEN"]

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("posts"))
async def posts_handler(message: Message) -> None:
    """

    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    
    """
    try:
        text = habrparser.getActualPost()
        print(text)
        await message.answer(text)
    except Exception as e:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("bot error: " + str(e))


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())