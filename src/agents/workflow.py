from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from src.agents.tools import analyst_tools, editor_tools
from yandex_chain import YandexLLM
from yandex_chain.YandexGPT import YandexGPTModel
import os

load_dotenv(".env")

# model
yandex_key = os.getenv("YANDEXGPT_API_KEY")
yandex_model = os.getenv("YANDEXGPT_MODEL")
yandex_folder = os.getenv("YANDEXGPT_FOLDER_ID")

# agents
supervisor_prompt = os.getenv("SUPERVISOR_AGENT_PROMPT")
analyst_prompt = os.getenv("ANALYST_AGENT_PROMPT")
editor_prompt = os.getenv("EDITOR_AGENT_PROMPT")

model = YandexLLM(
    folder_id=yandex_folder,
    api_key=yandex_key,
    model=YandexGPTModel(int(yandex_model))
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