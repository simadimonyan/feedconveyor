import os

from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.prompts import PromptTemplate
from langchain_gigachat.chat_models import GigaChat
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph_supervisor import create_supervisor

load_dotenv(".env")

# model
giga_key = os.getenv("GIGACHAT_API_KEY")
giga_model = os.getenv("GIGACHAT_MODEL")

# agent prompts
supervisor_prompt = os.getenv("SUPERVISOR_AGENT_PROMPT")
analyst_prompt = os.getenv("ANALYST_AGENT_PROMPT")
editor_prompt = os.getenv("EDITOR_AGENT_PROMPT")

# agents
analyst = None

client = MultiServerMCPClient(
    {
        "web": {
            "transport": "sse",
            "url": "http://mcp:8082/sse",
        }
    }
)

model = GigaChat(
        credentials=giga_key,
        model=giga_model,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
)

async def build_analyst():
    global analyst
    tools = await client.get_tools()
    tool_descriptions = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])

    prompt_template = PromptTemplate(
        input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
        template=analyst_prompt
    ).partial(
        tools=tool_descriptions,
        tool_names=tool_names,
        agent_scratchpad=""
    )

    analyst = create_react_agent(
        model=model,
        tools=tools,
        prompt=prompt_template,
        name="analyst"
    )
    return analyst

async def build_supervisor():
    global analyst
    if analyst is None:
        analyst = await build_analyst()

    supervisor = create_supervisor(
        agents=[analyst],
        model=model,
        prompt=supervisor_prompt
    )
    return supervisor

async def build_multi_agentic_system():
    supervisor = await build_supervisor()
    return supervisor.compile()