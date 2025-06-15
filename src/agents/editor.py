from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import StateGraph, START, END

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