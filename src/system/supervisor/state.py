from operator import add
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps

from src.domain.analytics import Content

class State(TypedDict, total=False):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    content: Annotated[list[Content], add]
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps


