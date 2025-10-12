New-Item -ItemType Directory -Force -Path .\scripts | Out-Null
@'
import os, asyncio, aiohttp
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff
from tenacity import retry, stop_after_attempt, wait_fixed

AGENTS = ["air", "ceo", "cfo", "clo", "cmo", "coo", "cos", "cto", "sec"]

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma:300m")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def detect_vector_size() -> int:
    async with aiohttp.ClientSession() as sess:
        try:
            r = await sess.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBEDDING_MODEL, "prompt": "hello world"})
            r.raise_for_status()
            data = await r.json()
            return len(data["embedding"])
        except Exception as e:
            print(f"Error detecting vector size: {e}")
            raise

def ensure_collections(vec_size: int):
    client = QdrantClient(url=QDRANT_URL)
    for a in AGENTS:
        name = f"agent_{a}_memory"
        try:
            client.get_collection(name)
            print(f"[OK] Collection exists: {name}")
        except Exception:
            print(f"[NEW] Creating collection: {name} (size={vec_size})")
            client.recreate_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vec_size, distance=Distance.COSINE),
                optimizers_config=OptimizersConfigDiff(indexing_threshold=20000),
            )

async def main():
    try:
        size = await detect_vector_size()
        print(f"Detected embedding size: {size}")
        ensure_collections(size)
    except Exception as e:
        print(f"Failed to bootstrap collections: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
'@ | Out-File -FilePath .\scripts\bootstrap_qdrant.py -Encoding utf8 -Force