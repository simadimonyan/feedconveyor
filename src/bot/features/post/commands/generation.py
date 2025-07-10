from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

@router.message(Command("generate"))
async def generate(message: Message) -> None:

    kb = [
        [InlineKeyboardButton(text="Новости Habr", callback_data="habr_news")],
        [InlineKeyboardButton(text="Agent", callback_data="agent")]
    ]

    await message.answer(
        "📢 Выберете тип генерации поста: ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

