from dotenv import load_dotenv
import requests
import json
import os

class AI():

    def __init__(self):
        load_dotenv("/app/.env")
        self.smm_prompt = os.getenv("SMM_PROMPT")
        self.ollama_url = os.getenv("OLLAMA_URL")

    def generatePostText(self, text):
        system_prompt = self.smm_prompt
        try:
            url = self.ollama_url
            data = {
                "model": "llama3",
                "prompt": f"{system_prompt} {text}",
                "stream": False
            }
            response = requests.post(url, json=data)
            if response.status_code == 200:
                response_text = response.text
                data = json.loads(response_text)
                actual_response = data["response"]
                return str(actual_response)
            return str(response["response"])
        
        except Exception as e:
            return f"Error ocurred on llm processing model: {e}"
        
    
    
        