from bs4 import BeautifulSoup
import feedparser
import requests

class Habr:

    def getNews():

        parser = feedparser.parse("https://habr.com/ru/rss/news/?fl=ru")

        title = parser.entries[0].title
        postLink = parser.entries[0].link
        response = requests.get(postLink)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ""
        for post in soup.find_all('p'):
            text += post.get_text()

        return (postLink, title, text)