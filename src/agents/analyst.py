from langchain_community.tools import DuckDuckGoSearchResults
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from src.domain.analitics import News, Trends, Content
from src.utills.parsers.analitics.tgstat import TGStat
from src.agents.workflow import analyst

from bs4 import BeautifulSoup
import requests
import json
import time

memory = MemorySaver() # checkpoint every node state

# DATA COLLECTION NODES

def web_search(state: Content):
    prompt_template = f"""
        Your task is to generate search queries for DuckDuckGo to find the latest and most relevant 
        information about a target audience for creating a Telegram post. Each query should be specific, 
        designed to uncover trends, news, or discussions related to the audience’s interests, behavior, or needs. 
        Language must be in target audience querry like.

        Here are the parameters for the task:
            •	Target Audience Description: {state["target_audience"]}
            •	Purpose: To gather insights, trends, or news that can inform a post tailored to this audience.
            •	Desired Content Types:
            •	Breaking news or recent developments.
            •	Trends in the audience’s area of interest.
            •	Common questions or discussions happening online.
            •	Innovative ideas or products targeting the audience.

        Answer just a list of 2 items of plaintext only without nummers like (1. 2.) or anything else not related to querry - JUST CLEAR TEXT in lowercase.
        DO NOT TYPE "Here are the search queries for DuckDuckGo:" or something like that

        Example:

        querry1
        querry2
    """

    generated_response = analyst.invoke({ "messages": [HumanMessage(content=prompt_template)]})
    search = DuckDuckGoSearchResults(output_format="list")
    response_text = generated_response["messages"][1].content
    lines_array = response_text.splitlines()
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
    
    return state

# DATA PROCESSING NODES 

def tganalytics(state: Content):
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

        Target Audience: {state['target_audience']}    

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
    
    prompt = f"""
        You are an analyst expert in creating engaging and relevant topics for Telegram posts.
        Your task is to generate a topic based on the target audience and the trends gathered from the analysis.

        Target Audience: {state['target_audience']}
        Trends: {state['analitics']}

        Generate a concise and appealing topic that would attract the target audience's attention.
        The topic should be relevant to the trends and interests of the audience.

        Answer just a single line of plaintext with the topic.
    """
    generated_response = analyst.invoke({ "messages": [HumanMessage(content=prompt)]})
    topic = generated_response["messages"][1].content.strip()
    state["post_topic"] = topic

    return state

def summarize(state: Content):

    prompt = f"""
        You are an analyst expert in summarizing content for Telegram posts.
        If you need extra context use tools.
        Your task is to create a concise summary based on the trends and the topic generated.
        Topic: {state['post_topic']}
        Target Audience: {state['target_audience']}
        Trends: {state['analitics']}
    """
    generated_response = analyst.invoke({ "messages": [HumanMessage(content=prompt)]})
    summary = generated_response["messages"][1].content.strip()
    state["summary"] = summary

    return state

def build_prompt(state: Content):
    pass

# GRAPH

builder = StateGraph(Content)
builder.add_node("web_search", web_search)
builder.add_node("tganalytics", tganalytics)
builder.add_node("summarize", summarize)
builder.add_node("generate_topic", generate_topic)
builder.add_node("build_prompt", build_prompt)

builder.add_edge(START, "web_search")
#builder.add_edge("tganalytics", "web_search")
builder.add_edge("web_search", "generate_topic")
builder.add_edge("generate_topic", "summarize")
builder.add_edge("summarize", "build_prompt")
builder.add_edge("build_prompt", END)

graph = builder.compile(memory)