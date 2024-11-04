
import requests
import json

class AI():

    def __init__(self):
        
        def load_data_from_json():
            try:
                with open('./configs/bot-config.json', 'r') as file:
                    data = json.load(file)
                    return data
            except FileNotFoundError:
                return {}

        config = load_data_from_json()
        print(f"Config: {config}") 

        self.smm_prompt = config["ai"]["SMM_PROMPT"]

    def generatePostText(self, text):

        system_prompt = self.smm_prompt
        print(system_prompt)
        print(text)

        try:

            url = 'http://host.docker.internal:11434/api/generate'
            data = {
                "model": "llama3",
                "prompt": system_prompt + " " + text,
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
        
    
    
        