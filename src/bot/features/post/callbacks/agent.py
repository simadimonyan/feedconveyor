from aiogram import F, Router
from aiogram.types import CallbackQuery
from langchain_core.runnables import RunnableConfig

from src.system.supervisor.workflow import build_multi_agentic_system

router = Router()

@router.callback_query(F.data == "agent")
async def post_handler(call: CallbackQuery) -> None:

    system = await build_multi_agentic_system()
    config = RunnableConfig(recursion_limit=100)
    async for chunk in system.astream(
        {"messages": [
            {"role": "user", "content": "Найди актуальные новости по андроид разработке и сделай отчет. Подготовь публикацию для Telegram-канала"}
        ]},
        stream_mode=["values"],
        subgraphs=True,
        config=config
    ):
        if isinstance(chunk, tuple) and len(chunk) == 3:
            path, mode, payload = chunk
            if isinstance(payload, dict):
                messages = payload.get("messages", [])
                if messages:
                    last_msg = messages[-1]
                    agent_name = path[0] if path else "UnknownAgent"
                    sender = last_msg.role if hasattr(last_msg, 'role') else "UnknownSender"
                    print(f"[{agent_name}][{sender}] {last_msg.content}", flush=True)
