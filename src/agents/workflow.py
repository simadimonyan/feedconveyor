from langchain_gigachat.chat_models import GigaChat
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from src.agents.tools import analyst_tools, editor_tools
import os

load_dotenv(".env")

# model
giga_key = os.getenv("GIGACHAT_API_KEY")
giga_model = os.getenv("GIGACHAT_MODEL")

# agents
supervisor_prompt = os.getenv("SUPERVISOR_AGENT_PROMPT")
analyst_prompt = os.getenv("ANALYST_AGENT_PROMPT")
editor_prompt = os.getenv("EDITOR_AGENT_PROMPT")

model = GigaChat(
    credentials=giga_key,
    model=giga_model,
    scope="GIGACHAT_API_PERS",
    verify_ssl_certs=False,
)

analyst = create_react_agent(
    model=model,
    tools=analyst_tools,
    name="Analyst",
    prompt=analyst_prompt
)

editor = create_react_agent(
    model=model,
    tools=editor_tools, 
    name="Editor",
    prompt=editor_prompt
)

supervisor = create_supervisor(
    [analyst],
    model=model,
    prompt=supervisor_prompt
)

supervisor.compile()