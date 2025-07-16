from langgraph_supervisor import create_handoff_tool

transfer_to_analyst = create_handoff_tool(
    agent_name="analyst",
    description="Передать задачу аналитику. Аналитик выполняет поиск и обрабатывает входные данные по целевой аудитории.",
    add_handoff_messages=True
)

transfer_to_editor = create_handoff_tool(
    agent_name="editor",
    description="Передать задачу редактору. Редактор выполняет подготовку обработанных данных в Телеграм пост.",
    add_handoff_messages=True
)
