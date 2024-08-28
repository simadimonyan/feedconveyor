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
from aiogram.types import LinkPreviewOptions

from fabrics.telegrampost import Post, PostType

dp = Dispatcher()

def load_data_from_json():
    try:
        with open('./configs/bot-config.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("posts"))
async def posts_handler(message: Message) -> None:
    try:
        post = Post()
        (link, text) = post.createPost(PostType.HABR_NEWS)
        print(text)
        preview = LinkPreviewOptions(
            url=link,
            prefer_large_media=True
        )
        await message.answer(text, parse_mode="HTML", link_preview_options=preview)
    except Exception as e:
        await message.answer("bot error: " + str(e))


async def main() -> None:
    config = load_data_from_json()
    TOKEN = config["telegram"]["API_TOKEN"]
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())