import asyncio
import os
import time

from dotenv import load_dotenv
from langchain.prompts.chat import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_gigachat.chat_models import GigaChat
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor, create_forward_message_tool

from src.system.mcp.client import client
from src.system.supervisor.handoffs import transfer_to_analyst, transfer_to_editor  # back_to_supervisor
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
    [
        SystemMessage(content=analyst_prompt),
        MessagesPlaceholder(variable_name="messages")
    ]
).partial(
    tools=tools,
    tool_names=tool_names,
    today=str(time.ctime(time.time()))
)

print(analyst_prompt_template)

def analyst_prompt():
    pass

analyst = create_react_agent(
    model=model,
     tools=tools, #+ [back_to_supervisor],
    state_schema=State,
    prompt=analyst_prompt_template,
    name="analyst"
)

editor_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessage(content=editor_prompt),
        MessagesPlaceholder(variable_name="messages")
    ]
)

print(editor_prompt_template)

editor = create_react_agent(
    model=model,
    tools=[],
    state_schema=State,
    prompt=editor_prompt_template,
    name="editor"
)

supervisor = create_supervisor(
    agents=[analyst, editor],
    model=model,
    tools=[transfer_to_analyst, transfer_to_editor, create_forward_message_tool("supervisor")],
    state_schema=State,
    add_handoff_messages=True,
    add_handoff_back_messages=True,
    prompt=supervisor_prompt,
    output_mode="full_history"
)

graph = supervisor.compile()