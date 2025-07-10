from aiogram import F, Router
from aiogram.types import CallbackQuery

from src.system.supervisor.workflow import build_multi_agentic_system

router = Router()

@router.callback_query(F.data == "agent")
async def post_handler(call: CallbackQuery) -> None:

    app = await build_multi_agentic_system()
    result = app.invoke({
        "messages": [
            {"role": "user", "content": "Найди актуальные новости по андроид разработке и сделай отчет. Подготовь публикацию для Telegram-канала"}
        ]
    })

    await call.message.answer(result['messages'][-1].content)
