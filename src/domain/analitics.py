import operator
from typing import Annotated, List
from pydantic import BaseModel
from typing_extensions import TypedDict

# SCHEMAS

class News(BaseModel):
    title: str
    date: str
    text: str
    link: str

class Trends(TypedDict):
    trends: List[News]

class Content(TypedDict):
    target_audience: str
    analitics: Annotated[List[Trends], operator.add]
    post_topic: str
    prompt: str
    summary: str