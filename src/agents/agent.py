from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langgraph.graph import MessagesState
from src.agents import tools
import os

load_dotenv(".env")
ollama_url = os.getenv("OLLAMA_BASE_URL")
ollama_model = os.getenv("OLLAMA_MODEL")

llm = ChatOllama(model=ollama_model, base_url=ollama_url)
llm_with_tools = llm.bind_tools(tools.tools_list)
memory = MemorySaver() #checkpoint every node state

# Node
def llm_call(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Build graphа
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)
builder.add_node("tools", ToolNode(tools.tools_list))

builder.add_edge(START, "llm_call")
builder.add_conditional_edges("llm_call", tools_condition)
builder.add_edge("tools", "llm_call")

graph = builder.compile(memory)