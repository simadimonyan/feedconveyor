from aiogram import F, Router
from aiogram.types import CallbackQuery

router = Router()

from src.bot.bot import bot, username, channel_id

@router.callback_query(F.data == "approve")
async def post_handler(call: CallbackQuery) -> None:
    try:
        await bot.copy_message(
            chat_id=channel_id,
            from_chat_id=call.message.chat.id,
            parse_mode="HTML",
            message_id=call.message.message_id
        )
        await call.message.answer(f"✅ Вы опубликовали новую запись в канале! {username}")
    except Exception as e:
        await call.message.answer(f"❌ Произошла ошибка при публикации записи: {str(e)}")