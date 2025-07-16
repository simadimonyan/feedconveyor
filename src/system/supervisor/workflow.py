import asyncio
import os
from typing import Literal

from dotenv import load_dotenv
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_gigachat.chat_models import GigaChat
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from src.system.mcp.client import client
from src.system.supervisor.handoffs import transfer_to_analyst, transfer_to_editor
from src.system.supervisor.state import State

load_dotenv(".env")

# model
giga_key = os.getenv("GIGACHAT_API_KEY")
giga_model = os.getenv("GIGACHAT_MODEL")

# agent prompts
supervisor_prompt = os.getenv("SUPERVISOR_AGENT_PROMPT")
analyst_prompt = os.getenv("ANALYST_AGENT_PROMPT")
editor_prompt = os.getenv("EDITOR_AGENT_PROMPT")

model = GigaChat(
    credentials=giga_key,
    model=giga_model,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
)

tools = asyncio.run(client.get_tools())

tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
tool_names = ", ".join([tool.name for tool in tools])
print(tool_descriptions)
print(tool_names)

analyst_prompt_template = ChatPromptTemplate.from_messages(
    [ ("system", analyst_prompt),
    MessagesPlaceholder(variable_name="messages")
]).partial(
    tools=tools,
    tool_names=tool_names
)

print(analyst_prompt_template)

def analyst_prompt():
    pass

analyst = create_react_agent(
    model=model,
    tools=tools,
    state_schema=State,
    prompt=analyst_prompt_template,
    name="analyst"
)

editor_prompt_template = ChatPromptTemplate.from_messages([
    ("system", editor_prompt),
    MessagesPlaceholder(variable_name="messages")
]).partial(
    tools=tools,
    tool_names=tool_names
)

print(editor_prompt_template)

editor = create_react_agent(
    model=model,
    state_schema=State,
    tools=tools,
    prompt=editor_prompt_template,
    name="editor"
)

supervisor = create_supervisor(
    agents=[analyst, editor],
    model=model,
    tools=[transfer_to_analyst, transfer_to_editor],
    state_schema=State,
    add_handoff_messages=True,
    add_handoff_back_messages=True,
    prompt=supervisor_prompt,
    output_mode="full_history"
).compile()

def router(state: State) -> Literal["analyst", "editor", END]:

    if state.get("remaining_steps", 0) <= 0:
        return END

    next_agent = state.get("next_agent", "analyst")

    if next_agent == "analyst":
        new_next = "editor"
    else:
        new_next = "analyst"

    return new_next

builder = StateGraph(State)

builder.add_node("analyst", analyst)
builder.add_node("editor", editor)
builder.add_node("supervisor", supervisor)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges("supervisor", router)
builder.add_edge("analyst", "supervisor")
builder.add_edge("editor", "supervisor")
builder.add_edge("supervisor", END)

graph = builder.compile()