from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions
from aiogram.types import CallbackQuery
from aiogram import F
from handlers.tpost import Post, PostType
from database.db import Database
import asyncio
import logging
import sys

from utills.parsers.habrnews import Habr

from dotenv import load_dotenv
import time
import os

dp = Dispatcher()

config = load_dotenv(".env")
token = os.getenv("API_TOKEN")
id = os.getenv("CHANNEL_ID")
username = os.getenv("CHANNEL_USERNAME")

bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# COMMANDS

@dp.message(Command("generate"))
async def generate(message: Message) -> None:
    kb = [
        [InlineKeyboardButton(text="Новости Habr", callback_data="habr_news")],
        [InlineKeyboardButton(text="Agent", callback_data="agent")]
    ]
    await message.answer("📢 Выберете тип генерации поста: ", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


# CALLBACKS


# HABR PARSE BUTTON

@dp.callback_query(F.data == "habr_news")
async def post_handler(call: CallbackQuery) -> None:
    await call.message.edit_text("⏳ Генерирую новость, это займет какое-то время...")

    kb = [
        [InlineKeyboardButton(text=" 🔄 ", callback_data="habr_news")],
        [InlineKeyboardButton(text=" Опубликовать ", callback_data="approve")]
    ]
    
    try:    
        post = Post()
        (link, text) = post.createPost(PostType.HABR_NEWS)
        print(text)
        preview = LinkPreviewOptions(
            url=link,
            prefer_large_media=True
        )
        try: 
            await call.answer('Генерация завершена', show_alert=False) 
        except: 
            await call.message.answer('Генерация завершена', show_alert=False) 
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
                                  link_preview_options=preview)
    except Exception as e:
        await call.message.answer("bot error: " + str(e))


# POST PUBLICATION APPROVAL BUTTON

@dp.callback_query(F.data == "approve")
async def post_handler(call: CallbackQuery) -> None:
    try:
        await bot.copy_message(
            chat_id=id,
            from_chat_id=call.message.chat.id,
            parse_mode="HTML",
            message_id=call.message.message_id
        )
        await call.message.answer(f"✅ Вы опубликовали новую запись в канале! {username}")
    except Exception as e:
        await call.message.answer(f"❌ Произошла ошибка при публикации записи: {str(e)}")


# AI AGENT BUTTON

@dp.callback_query(F.data == "agent")
async def post_handler(call: CallbackQuery) -> None:

    db = Database()

    postLink, title, text = Habr.getNews()
    date = time.ctime(time.time())

    data = {"date": date, "title": title, "source_link": postLink, "text": text}

    await db.store_data(data)
    await call.message.answer(f"done")
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(dp.start_polling(bot))
