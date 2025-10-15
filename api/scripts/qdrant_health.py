import requests

def check_qdrant():
    try:
        res = requests.get("http://localhost:6333/collections")
        return {
            "status": "connected" if res.ok else "unreachable",
            "collections": res.json().get("result", [])
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
