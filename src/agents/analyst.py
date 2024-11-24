import json
import operator
from typing import Annotated, List
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools import DuckDuckGoSearchResults
from pydantic import BaseModel
import requests
from typing_extensions import TypedDict
import time 
import logging
import os

from src.database.db import Database

load_dotenv(".env")
ollama_url = os.getenv("OLLAMA_BASE_URL")
ollama_model = os.getenv("OLLAMA_MODEL")

analyst = ChatOllama(model=ollama_model, base_url=ollama_url)
memory = MemorySaver() # checkpoint every node state

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

# DATA COLLECTION NODES

def news_search(state: Content):
    pass

def web_search(state: Content):
    prompt_template = f"""
        Your task is to generate search queries for DuckDuckGo to find the latest and most relevant 
        information about a target audience for creating a Telegram post. Each query should be specific, 
        designed to uncover trends, news, or discussions related to the audience’s interests, behavior, or needs.

        Here are the parameters for the task:
            •	Target Audience Description: {state["target_audience"]}
            •	Purpose: To gather insights, trends, or news that can inform a post tailored to this audience.
            •	Desired Content Types:
            •	Breaking news or recent developments.
            •	Trends in the audience’s area of interest.
            •	Common questions or discussions happening online.
            •	Innovative ideas or products targeting the audience.

        Answer just a list of 2 items of plaintext only without nums or anything else not related to querry.
        DO NOT TYPE "Here are the search queries for DuckDuckGo:" or something like that
    """

    generated_response = analyst.invoke(prompt_template) 
    search = DuckDuckGoSearchResults(output_format="list")
    lines_array = generated_response.content.splitlines()
    news_trends = []

    for item in lines_array:
        webs = search.invoke(item)

        for web in webs:
            try:
                response = requests.get(web["link"])
                soup = BeautifulSoup(response.text, 'html.parser')
                text = ""
                for post in soup.find_all('p'):
                    text += post.get_text()
                    
                news = News(title=web["title"], text=text, link=web["link"], date=str(time.ctime(time.time())))
                news_trends.append(news)
            except:
                continue
        
    trends = Trends(trends=news_trends)

    if "analitics" in state and state["analitics"] is not None:
        state["analitics"].append(trends)
    else:
        state["analitics"] = [trends]

    state["target_audience"] = state["target_audience"]
    
    return 


def rag_search(state: Content):
    db = Database()
    response = db.search(f"Find related news about {state['target_audience']} for the last 24h - now is {time.ctime(time.time())}")
    
    prompt_template = """
        Here is a list of news items in the format "title | date | text | link":
        {data}

        Your task is to extract each news item into the following JSON format:
        - title: (string)
        - date: (string)
        - text: (string)
        - link: (string)

        Answer as a code with the result as a JSON syntax-only (but as a plaintext) array without any other words.
        DO NOT TYPE ```json ``` 
    """

    prompt = prompt_template.format(data=response) 
    generated_response = analyst.invoke(prompt) 

    news_items = json.loads(str(generated_response.content))

    parsed_news = []
    for item in news_items:
        news = News(
            title=item["title"],
            date=item["date"],
            text=item["text"],
            link=item["link"]
        )
        parsed_news.append(news)

    trends = Trends(trends=parsed_news)
    
    if "analitics" in state and state["analitics"] is not None:
        state["analitics"].append(trends)
    else:
        state["analitics"] = [trends]

    state["target_audience"] = state["target_audience"]

    return state


# DATA PROCESSING NODES 

def summarize(state: Trends) -> Content:

    pass

def generate_topic(state: Content):
    pass

def build_prompt(state: Content):
    pass


# GRAPH

builder = StateGraph(Content)
builder.add_node("news_search", news_search)
builder.add_node("web_search", web_search)
builder.add_node("rag_search", rag_search)
builder.add_node("summarize", summarize)
builder.add_node("generate_topic", generate_topic)
builder.add_node("build_prompt", build_prompt)

builder.add_edge(START, "news_search")
builder.add_edge(START, "web_search")
builder.add_edge(START, "rag_search")
builder.add_edge("news_search", "summarize")
builder.add_edge("web_search", "summarize")
builder.add_edge("rag_search", "summarize")
builder.add_edge("summarize", "generate_topic")
builder.add_edge("generate_topic", "build_prompt")
builder.add_edge("build_prompt", END)

graph = builder.compile(memory)