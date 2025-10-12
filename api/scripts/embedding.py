import requests

def get_embedding(text: str):
    response = requests.post(
        'http://localhost:11434/api/embeddings',
        json={'model': 'embeddinggemma:300m', 'prompt': text}
    )
    return response.json()['embedding']