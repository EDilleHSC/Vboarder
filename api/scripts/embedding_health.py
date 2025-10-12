import requests

def check_embedding_service():
    try:
        response = requests.get("http://localhost:11434")  # Ollama's typical port
        return {
            "status": "up" if response.ok else "down",
            "http_status": response.status_code
        }
    except Exception as e:
        return {"status": "down", "error": str(e)}
