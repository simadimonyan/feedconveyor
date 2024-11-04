from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions
from aiogram.types import CallbackQuery
from aiogram import F

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



@dp.callback_query(F.data == "habr_news")
async def post_handler(call: CallbackQuery) -> None:
    await call.message.edit_text('Генерирую новость, это займет какое-то время...')

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
        await call.answer('Генерация завершена', show_alert=False)
        await call.message.edit_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb),
                                  link_preview_options=preview)
    except Exception as e:
        await call.message.answer("bot error: " + str(e))


async def main() -> None:
    config = load_data_from_json()
    TOKEN = config["telegram"]["API_TOKEN"]
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())