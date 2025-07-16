from operator import add
from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep, RemainingSteps
from src.domain.analytics import Content

class State(TypedDict, total=False):
    input: Annotated[list[str], add]
    messages: Annotated[list, add_messages]
    content: Annotated[list[Content], add]
    is_last_step: IsLastStep
    remaining_steps: RemainingSteps
    agent_scratchpad: Annotated[list[str], add]
    next_agent: Optional[str]
