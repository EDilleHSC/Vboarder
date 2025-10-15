import requests
response = requests.post(
    'http://localhost:11434/api/embeddings',
    json={'model': 'embeddinggemma:300m', 'prompt': 'test'}
)
print(f"Dimensions: {len(response.json()['embedding'])}")
