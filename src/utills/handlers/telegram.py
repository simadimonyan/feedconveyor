from src.utills.parsers.web.habr import Habr
from src.utills.handlers.ai import AIDirectCall
from enum import Enum

ai = AIDirectCall()

class PostType(Enum):
    HABR_NEWS = 1,
    AGENT_AI = 2

class Post:

    def __init__(self):
        self.channel = "<a href=\"https://t.me/digit_code\">ЦифроКод: AI&IT 🖥</a>"
        self.title = ""
        self.postLink = ""
        self.text = ""
        self.credentials = ""

    def createPost(self,type: PostType):
        match type:
            case PostType.HABR_NEWS:
                (self.postLink, self.title, self.text) = Habr.getNews()
                self.text = ai.generatePostText(self.text)
                self.credentials = f"""🌐 | {self.channel} | <a href="{self.postLink}">Источник 📢</a> """

        return (self.postLink, f"""
        <b>{self.title}</b> \n\n {self.text} \n\n {self.credentials}
        """)