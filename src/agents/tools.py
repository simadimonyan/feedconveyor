from src.database.db import Database
from src.parsers.habrnews import Habr
from langchain.agents import tool

@tool
def habr():
    """
    - Returns the last IT news article on Habr
    """
    return Habr.getNews()

@tool
def news_database():
    """
    - Returns data about news querry from the vector database
    """
    db = Database()
    return db.search("News for the last 24h")

# AGENT TOOLS SET
editor = [news_database]
analyst = []
expert = []