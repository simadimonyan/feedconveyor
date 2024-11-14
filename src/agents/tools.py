from src.database.db import Database
from src.parsers.habrnews import Habr
from langchain.agents import tool
import time

@tool
def habr():
    """
    - Returns the last IT news article on Habr
    """
    return Habr.getNews()

@tool
async def news_database():
    """
    - Returns data about news querry from the vector database
    """
    db = Database()
    return await db.search(f"News for the last 24h - now {time.ctime(time.time())}")

# list of tools
tools_list = [news_database]
