import requests

API_URL = "https://api.deepseek.com/v1/chat/completions"  # Verifique o endpoint na documentação
API_KEY = "sk-d00b8d02cdba40e1b6717ffcbf308dd5"  # Substitua pela sua chave

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "deepseek-chat",  # Verifique o modelo correto na documentação
    "messages": [
        {"role": "user", "content": "Explique o que é uma API em 50 palavras."}
    ],
    "temperature": 0.7
}

response = requests.post(API_URL, json=data, headers=headers)
print(response.json())