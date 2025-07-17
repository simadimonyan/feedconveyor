from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from langchain_core.messages import convert_to_messages, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.system.supervisor.state import State as AgentState
from src.system.supervisor.workflow import graph

router = Router()

class TaskState(StatesGroup):
    waiting_for_task = State()

@router.callback_query(F.data == "agent")
async def post_handler(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("📋 Отправьте целевую аудиторию для генерации поста.")
    await state.set_state(TaskState.waiting_for_task)
    await call.answer()

@router.message(TaskState.waiting_for_task)
async def handle_task(message: Message, state: FSMContext) -> None:
    task_text = message.text or message.caption
    if not task_text:
        await message.answer("Не удалось найти текст задачи. Отправьте, пожалуйста, ещё раз.")
        return

    await state.clear()
    await message.answer("⏳ Выполняю задачу, это может занять некоторое время...")

    config = RunnableConfig(recursion_limit=10)
    last_message = None

    async for chunk in graph.astream(
        AgentState(messages=[HumanMessage(content=task_text)], content=[]),
        stream_mode=["values"],
        subgraphs=True,
        config=config
    ):
        pretty_print_messages(chunk)

        if isinstance(chunk, tuple) and len(chunk) == 3:
            update_payload = chunk[2]
            for node_update in update_payload.values():
                messages = convert_to_messages(
                    node_update.get("messages", []) if isinstance(node_update, dict) else node_update
                )
                if messages:
                    last_message = messages[-1].content

    await message.answer(last_message or "Не удалось получить результат.")

def pretty_print_message(message, indent=False):
    def fix_separator(line):
        if "Message" in line and line.strip().startswith("="):
            parts = line.strip().split("Message")
            base = (parts[0].rstrip("=") + "Message" + parts[1]).strip()
            return "\n" + base.center(140, "=") + "\n"
        return line

    pretty = message.pretty_repr(html=True)
    pretty = "\n".join(fix_separator(line) for line in pretty.split("\n"))
    for line in pretty.split("\n"):
        print(line)

def pretty_print_messages(update):
    if isinstance(update, tuple) and len(update) == 3:
        ns, stream_type, payload = update
        if stream_type != "values":
            return
        print(f"Update from {'subgraph ' + ns[-1].split(':')[0] if ns else 'main graph'}:\n")
        update = payload
    else:
        print("Unexpected update structure:", repr(update))
        return

    for node_name, node_update in update.items():
        print(f"Update from node {node_name}:\n")
        messages = convert_to_messages(
            node_update.get("messages", []) if isinstance(node_update, dict) else node_update
        )
        for m in messages:
            pretty_print_message(m, indent=bool(ns))
        print()