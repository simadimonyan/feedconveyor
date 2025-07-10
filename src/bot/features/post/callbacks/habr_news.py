from aiogram import F, Router

from aiogram.types import(
    CallbackQuery,
    InlineKeyboardButton,
    LinkPreviewOptions,
    InlineKeyboardMarkup
)

from src.bot.handlers.telegram import PostType, Post

router = Router()

@router.callback_query(F.data == "habr_news")
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

        await call.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
            link_preview_options=preview
        )

    except Exception as e:
        await call.message.answer("bot error: " + str(e))