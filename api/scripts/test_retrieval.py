import os
import sys
import asyncio
import aiohttp
import time
import numpy as np
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma:300m")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", 5))

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def embed_query(text: str):
    async with aiohttp.ClientSession() as sess:
        try:
            r = await sess.post(f"{OLLAMA_URL}/api/embeddings", json={"model": EMBEDDING_MODEL, "prompt": text})
            r.raise_for_status()
            embedding = (await r.json())["embedding"]
            norm_embedding = np.array(embedding) / np.linalg.norm(embedding)
            return norm_embedding.tolist()  # Normalize to unit length
        except Exception as e:
            print(f"Embedding error: {e}")
            raise

async def search(agent: str, question: str, top_k: int = RAG_TOP_K):
    start_time = time.time()
    vec = await embed_query(question)
    collection = f"agent_{agent.lower()}_memory"
    client = QdrantClient(url=QDRANT_URL)
    hits = client.query_points(collection_name=collection, query=vec, limit=top_k).points
    if not hits:
        print("No results.")
        return
    for h in hits:
        p = h.payload or {}
        print(f"- {p.get('doc_name', '?')} (score={h.score:.3f})")
        print((p.get('content', '')[:300]).replace("\n", " ") + "...\n")
    print(f"Search completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python scripts\\test_retrieval.py <agent> \"<question>\"")
        sys.exit(1)
    asyncio.run(search(sys.argv[1], sys.argv[2]))
