from dotenv import load_dotenv
import requests
import json
from langchain_gigachat.chat_models import GigaChat
import os

class AIDirectCall():

    def __init__(self):
        load_dotenv(".env")
        self.smm_prompt = os.getenv("SMM_PROMPT")
        self.giga_model = os.getenv("GIGACHAT_MODEL")
        self.giga_key = os.getenv("GIGACHAT_API_KEY")

    def generatePostText(self, text):
        system_prompt = self.smm_prompt
        try:
            giga = GigaChat(
                credentials=self.giga_key,
                model=self.giga_model,
                scope="GIGACHAT_API_PERS",
                verify_ssl_certs=False,
            )       
            return giga.invoke([ {"role": "system", "content": f"{system_prompt} {text}"}]).content
        except Exception as e:
            return f"Error ocurred on llm processing model: {e}"
        
    
    
        