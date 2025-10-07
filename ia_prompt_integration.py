import json
import requests

def extrair_reasoning(resposta):
    """
    Extrai o reasoning da resposta de uma LLM.
    para isso a resposta contem <think> e </think> que delimitam o reasoning.
    a funçao retorna dois valores:
    - o reasoning extraido
    - a resposta sem o reasoning
    para o resta da resposta retirar toda quebra de linha e espacos em branco entre a tag <think> e a primeira letra da resposta
    """
    start_tag = "<think>"
    end_tag = "</think>"
    
    start_index = resposta.find(start_tag)
    end_index = resposta.find(end_tag)
    
    if start_index != -1 and end_index != -1 and start_index < end_index:
        reasoning = resposta[start_index + len(start_tag):end_index].strip()
        restante_resposta = (resposta[:start_index] + resposta[end_index + len(end_tag):]).strip()
        restante_resposta = ' '.join(restante_resposta.split())
        return reasoning, restante_resposta
    else:
        return None, resposta


class IAIntegration:
    
    def __init__(self):
        self.API_KEY = json.load(open('config.json'))['API_KEY']
        self.API_URL = 'https://llm.ic.unicamp.br/api/chat/completions'
        self.response = None

    def get_headers(self):
        return {
            'Authorization': f'Bearer {self.API_KEY}',
            'Content-Type': 'application/json'
        }

    def get_payload(self, prompt):
        return {
            "model": "deepseek-r1:14b",
            "messages": [{"role": "user", "content": prompt}]
        }
    
    def get_time_execution(self):
        return self.response["usage"]["approximate_total"]
    
    def get_tokens_used(self):
        return self.response["usage"]["total_tokens"]

    def get_motivation_stop(self):
        return self.response["choices"][0]["finish_reason"]

    def execute_prompt(self, prompt):
        headers = self.get_headers()
        payload = self.get_payload(prompt)
        response = requests.post(self.API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            self.response = response.json()
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        
    def fetch_response(self, prompt):
        headers = self.get_headers()
        payload = self.get_payload(prompt)
        response = requests.post(self.API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            self.response = response.json()
            return extrair_reasoning(self.response['choices'][0]['message']['content'])
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        


if __name__ == "__main__":
    ia = IAIntegration()
    prompt = "Some 2 + 2 , explique o raciocinio matematico"
    reasoning , response = ia.fetch_response(prompt)
    print("Response from IA:", response)
    print("Reasoning:", reasoning)