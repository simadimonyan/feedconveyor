from ollama import Client

import requests
import ollama
import json

API_TOKEN = ""

def load_data_from_json():
    try:
        with open('./configs/bot-config.json', 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {}
    
def init():
    config = load_data_from_json()
    API_TOKEN = config["ai"]["API_TOKEN"]

def managePost(text):
    print(text)
    try:
        system_content = "Ты российский SMM менеджер, твоя задача сделать небольшой пост на на рускком языке по текстовке которую отправил издатель, тебе нужно убрать все элементы которые говорят о том чей это пост и откуда, ты его переделываешь но название оставляешь таким же, каким и получил, выписываешь суть и чуть чуть добавляешь смайликов как реакцию, их добавлять везде не нужно только в начале абзаца"
        
        url = 'http://host.docker.internal:11434/api/generate'
        data = {
            "model": "llama3",
            "prompt": system_content + " " + text,
            "stream": False
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            response_text = response.text
            data = json.loads(response_text)
            actual_response = data["response"]
            print(actual_response)
            return str(actual_response)
        return str(response["response"])
    except Exception as e:
        text = str(e)
        return "ai error:  " + text
