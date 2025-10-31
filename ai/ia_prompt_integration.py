import json
import requests
import logging

logger = logging.getLogger(__name__)


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
        # extrai o conteúdo entre as tags, preservando quebras de linha internas
        reasoning_raw = resposta[start_index + len(start_tag):end_index]
        # normaliza CRLF/CR para LF e remove espaços nas extremidades
        reasoning = reasoning_raw.replace('\r\n', '\n').replace('\r', '\n').strip()

        # parte antes e depois das tags
        prefix = resposta[:start_index]
        suffix = resposta[end_index + len(end_tag):]

        # remover APENAS uma quebra de linha imediatamente após </think>
        if suffix.startswith('\r\n'):
            suffix = suffix[2:]
        elif suffix.startswith('\n') or suffix.startswith('\r'):
            suffix = suffix[1:]

        restante_resposta = prefix + suffix

        return reasoning, restante_resposta
    else:
        return None, resposta


class IAIntegration:
    
    def __init__(self):
        self.API_KEY = json.load(open('resources/config.json'))['API_KEY']
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
        max_retries = 3
        if response.status_code == 200:
            self.response = response.json()
            extract_reasoning = self.response['choices'][0]['message'].get('reasoning_content')
            resposta = self.response['choices'][0]['message'].get('content')
            logger.debug("Extracted reasoning: %s", extract_reasoning)
            logger.debug("Full response content: %s", resposta)
            return extract_reasoning, resposta
        else:
            for retry in range(max_retries):
                response = requests.post(self.API_URL, headers=headers, json=payload)
                if response.status_code == 200:
                    self.response = response.json()
                    extract_reasoning = self.response['choices'][0]['message'].get('reasoning_content')
                    resposta = self.response['choices'][0]['message'].get('content')
                    logger.debug("Extracted reasoning: %s", extract_reasoning)
                    logger.debug("Full response content: %s", resposta)
                    return extract_reasoning, resposta
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")
        
if __name__ == "__main__":
    # Script de teste rápido da integração com a API do LLM
    ia = IAIntegration()
    prompt = "Some 2 + 2 , explique o raciocinio matematico"
    try:
        reasoning , response = ia.fetch_response(prompt)
        logger.info("Response from IA: %s", response)
        logger.info("Reasoning: %s", reasoning)
    except Exception as e:
        logger.exception("Erro ao buscar resposta do LLM: %s", e)