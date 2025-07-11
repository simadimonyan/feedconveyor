from aiogram import F, Router
from aiogram.types import CallbackQuery
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import convert_to_messages

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
        pretty_print_messages(chunk)


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