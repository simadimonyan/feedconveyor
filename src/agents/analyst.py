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
import os

from parsers.tgstat import TGStat
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

def summarize(state: Content):
    buttons = TGStat.get_categories()
    filters = TGStat.get_filters()

    prompt = f"""
        We have information about the buttons on a webpage and the 
        target audience with specific interests. We need to select one
        of the buttons that corresponds to the target audience's interests 
        and then provide Selenium selectors for clicking that button.
        {buttons} {filters}

        Target Audience: {state['target_audience']}

        Here is a list of buttons:
        1. Text: "By Views", Link: "/ratings/posts/pt?sort=views"
        2. Text: "By Forwards", Link: "/ratings/posts/pt?sort=forwards"
        3. Text: "By Comments", Link: "/ratings/posts/pt?sort=comments"
        4. Text: "By Channel Reposts", Link: "/ratings/posts/pt?sort=quotes"
        5. Text: "By Reactions", Link: "/ratings/posts/pt?sort=reactions"

        Task:
        - Generate URL that best matches the target audience's interests for 5 types the list of buttons 
        
        The response should contain just only url lines for parsing:
        URL https path for your target audience category 
    """

    response = analyst.invoke(prompt)
    lines_array = response.content.splitlines()
    
    stats = []
    for url in lines_array:
        page = BeautifulSoup(url, 'html.parser')
        stats.append(page)

    prompt = f"""
        You have an object with trends, and statistics from other Telegram channels.
        Your task is to select the 3 most popular news items from the trends by analysing statistics. 
        Each news item should be returned in the format of News, which includes:
            1.	title — the title of the news.
            2.	date — the date of the news in YYYY-MM-DD HH:MM:SS format.
            3.	text — a brief description of the news or a summary.
            4.	link — the URL or source link to the news article.

        Trends: {state['analitics']}

        Analitics: {stats}

        Your task is to extract each news item into the following JSON format:
        - title: (string)
        - date: (string)
        - text: (string)
        - link: (string)

        Answer as a code with the result as a JSON syntax-only (but as a plaintext) array without any other words.
        DO NOT TYPE ```json ``` 
    """

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
    
    state["analitics"] = [trends]
    state["target_audience"] = state["target_audience"]

    return state

def generate_topic(state: Content):
    pass

def build_prompt(state: Content):
    pass


# GRAPH

builder = StateGraph(Content)
builder.add_node("web_search", web_search)
builder.add_node("rag_search", rag_search)
builder.add_node("summarize", summarize)
builder.add_node("generate_topic", generate_topic)
builder.add_node("build_prompt", build_prompt)

builder.add_edge(START, "web_search")
builder.add_edge(START, "rag_search")
builder.add_edge("news_search", "summarize")
builder.add_edge("web_search", "summarize")
builder.add_edge("rag_search", "summarize")
builder.add_edge("summarize", "generate_topic")
builder.add_edge("generate_topic", "build_prompt")
builder.add_edge("build_prompt", END)

graph = builder.compile(memory)