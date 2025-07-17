from typing import Annotated

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId, BaseTool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langgraph_supervisor.handoff import METADATA_KEY_HANDOFF_DESTINATION


def create_custom_handoff_tool(*, agent_name: str, description: str | None) -> BaseTool:

    @tool(agent_name, description=description)
    def handoff_to_agent(
        task_description: Annotated[str, "Поставь задачу следующему агенту в виде промпта, что ему нужно сделать на основе его фунционала"],
        state: Annotated[dict, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId],
    ):
        tool_message = ToolMessage(
            content=f"Successfully transferred to {agent_name}",
            name=agent_name,
            tool_call_id=tool_call_id,
        )
        messages = state["messages"]
        return Command(
            goto=agent_name,
            graph=Command.PARENT,
            update={
                "messages": messages + [tool_message],
                "task_description": task_description,
            },
        )

    handoff_to_agent.metadata = {METADATA_KEY_HANDOFF_DESTINATION: agent_name}
    return handoff_to_agent

transfer_to_analyst = create_custom_handoff_tool(
    agent_name="analyst",
    description="Передать задачу аналитику. Аналитик выполняет поиск последних новостей по целевой аудитории."
)

transfer_to_editor = create_custom_handoff_tool(
    agent_name="editor",
    description="Передать задачу редактору. Редактор выполняет подготовку новостей в Телеграм пост.",
)

