from src.database.db import Database
from src.bot.handlers.habr import getNews
from langchain.agents import tool

@tool
def habr():
    """
    - Returns the last IT news article on Habr
    """
    return getNews()



@tool
def domain_database():
    """
    - Returns data about domain querry from the vector database
    """
    db = Database()
    return db.search("")

# AGENT TOOLS SET

editor_tools = []
analyst_tools = [habr]
expert_tools = [domain_database]