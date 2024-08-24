from handlers import ai

import feedparser
import ssl

def getActualPost():

    #context = ssl._create_default_https_context = ssl._create_unverified_context

    parser = feedparser.parse("https://habr.com/ru/rss/news/?fl=ru")
    first_post_link = parser.entries[0].link

    return ai.managePost(f'''{first_post_link}''') + ""
