from enum import Enum

from fabrics.habrnews import Habr
from fabrics.ai import AI

class PostType(Enum):
    HABR_NEWS = 1

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
                ai = AI()
                self.text = ai.generatePostText(self.text)
                self.credentials = f"""🌐 | {self.channel} | <a href="{self.postLink}">Источник 📢</a> """

        return (self.postLink, f"""
        <b>{self.title}</b> \n\n {self.text} \n\n {self.credentials}
        """)