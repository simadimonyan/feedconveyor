from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import convert_to_messages

from src.system.supervisor.workflow import build_multi_agentic_system

router = Router()

class TaskState(StatesGroup):
    waiting_for_task = State()

@router.callback_query(F.data == "agent")
async def post_handler(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.answer("📋 Пришлите задачу текстом и я её выполню.")
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

    system = await build_multi_agentic_system()
    config = RunnableConfig(recursion_limit=100)
    last_message = None

    async for chunk in system.astream(
        {"messages": [
            {"role": "user", "content": task_text}
        ]},
        stream_mode=["values"],
        subgraphs=True,
        config=config
    ):
        pretty_print_messages(chunk)
        if isinstance(chunk, tuple) and len(chunk) == 3:
            _, _, update_payload = chunk
            for node_update in update_payload.values():
                if isinstance(node_update, dict):
                    messages = convert_to_messages(node_update.get("messages", []))
                elif isinstance(node_update, list):
                    messages = convert_to_messages(node_update)
                else:
                    continue
                if messages:
                    last_message = messages[-1].content

    if last_message:
        await message.answer(last_message)
    else:
        await message.answer("Не удалось получить результат.")


def pretty_print_message(message, indent=False):
    def fix_separator(line):
        if "Message" in line and line.strip().startswith("="):
            parts = line.strip().split("Message")
            left = parts[0].rstrip("=")
            base = (left + "Message" + parts[1]).strip()
            return "\n" + base.center(140, "=") + "\n"
        return line

    pretty_message = message.pretty_repr(html=True)
    if indent:
        pretty_message = "\n".join("" + c for c in pretty_message.split("\n"))
    pretty_message = "\n".join(fix_separator(line) for line in pretty_message.split("\n"))
    lines = pretty_message.split("\n")
    for i, line in enumerate(lines):
        print(line)
        # Добавить пустую строку только между логическими блоками (заголовок и обычный текст)
        if line.strip().startswith("="):
            # Если следующая строка не заголовок и не пустая
            if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].strip().startswith("="):
                print()


def pretty_print_messages(update, last_message=False):
    is_subgraph = False

    # Проверяем, что пришёл кортеж из трёх элементов: namespace tuple, stream type, и payload dict
    if isinstance(update, tuple) and len(update) == 3:
        ns_tuple, stream_type, update_payload = update
        # Следим только за нужным типом (например 'values'), если надо
        if stream_type != "values":
            return

        ns = ns_tuple  # namespace как tuple
        if ns:
            graph_id = ns[-1].split(":")[0]
            print(f"Update from subgraph {graph_id}:\n")
            is_subgraph = True
        else:
            print("Update from main graph:\n")
        update = update_payload  # затем работаем с payload
    else:
        # Если структура неожиданная — логируем и прекращаем
        print("Unexpected update structure:", repr(update))
        return

    # update теперь — словарь node_name → node_update
    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        print(update_label + "\n")

        if isinstance(node_update, dict):
            messages = convert_to_messages(node_update.get("messages", []))
        elif isinstance(node_update, list):
            messages = convert_to_messages(node_update)
        else:
            print("Unexpected node_update type:", type(node_update))
            return
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")