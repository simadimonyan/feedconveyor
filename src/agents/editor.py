from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition
from langgraph.graph import MessagesState
from src.agents.workflow import editor

memory = MemorySaver() #checkpoint every node state

# Node
def llm_call(state: MessagesState):
    return {"messages": [editor.invoke(state["messages"])]}

# Build graph
builder = StateGraph(MessagesState)
builder.add_node("llm_call", llm_call)

builder.add_edge(START, "llm_call")
builder.add_edge("llm_call", END)

graph = builder.compile(memory)