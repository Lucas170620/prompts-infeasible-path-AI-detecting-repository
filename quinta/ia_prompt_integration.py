import json
import requests



class IAIntegration:
    
    def __init__(self):
        self.API_KEY = json.load(open('config.json'))['API_KEY']
        self.API_URL = 'https://openrouter.ai/api/v1/chat/completions'

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.API_KEY}',
            'Content-Type': 'application/json',
            "HTTP-Referer": "https://openrouter.ai/",
            "X-Title": "OpenRouter Python SDK Example"
        }

    def get_payload(self, prompt):
        return {
            "model": "deepseek/deepseek-chat-v3.1:free",
            "messages": [{"role": "user", "content": prompt}]
        }
    
    def fetch_response(self, prompt):
        headers = self.get_headers()
        payload = self.get_payload(prompt)
        response = requests.post(self.API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")