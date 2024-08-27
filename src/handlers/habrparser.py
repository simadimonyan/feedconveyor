from handlers import ai
from bs4 import BeautifulSoup

import feedparser
import requests

def getActualPost():

    #context = ssl._create_default_https_context = ssl._create_unverified_context

    parser = feedparser.parse("https://habr.com/ru/rss/news/?fl=ru")

    title = parser.entries[0].title
    postLink = parser.entries[0].link

    response = requests.get(postLink)
    soup = BeautifulSoup(response.text, 'html.parser')

    text = ""
    for post in soup.find_all('p'):
        text += post.get_text()

    return ai.managePost(f'''{title} \n\n {text}''') + ""
