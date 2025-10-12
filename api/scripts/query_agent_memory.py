"""
query_agent_memory.py - Agent Memory Query Interface
Query an agent's Qdrant memory using semantic similarity
"""

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
import requests
import sys
import time

# Configuration
OLLAMA_URL = "http://localhost:11434/api/embeddings"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBED_MODEL = "embeddinggemma:300m"
DEFAULT_TOP_K = 5

# Initialize client
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def get_embedding(text: str, model: str = EMBED_MODEL) -> list:
    """Generate embedding vector using Ollama"""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": text},
            timeout=5  # Reduced from 20s
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except requests.Timeout:
        print(f"ERROR: Ollama request timed out (>{5}s). Is Ollama running?")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"ERROR: Cannot connect to Ollama at {OLLAMA_URL}")
        print(f"Details: {e}")
        sys.exit(1)


def collection_exists(collection_name: str) -> bool:
    """Check if Qdrant collection exists"""
    try:
        client.get_collection(collection_name)
        return True
    except UnexpectedResponse:
        return False


def query_agent(agent_name: str, query_text: str, top_k: int = DEFAULT_TOP_K, silent: bool = False) -> list:
    """Query agent's memory collection"""
    start_time = time.time()
    collection = f"agent_{agent_name.lower()}_memory"

    # Validate collection exists
    if not collection_exists(collection):
        print(f"ERROR: Agent '{agent_name}' has no memory collection")
        print(f"Collection '{collection}' not found in Qdrant")
        print(f"\nAvailable agents:")
        try:
            collections = client.get_collections().collections
            for c in collections:
                if c.name.startswith("agent_") and c.name.endswith("_memory"):
                    agent = c.name.replace("agent_", "").replace("_memory", "").upper()
                    print(f"  - {agent}")
        except:
            print("  (Unable to list collections)")
        return []

    # Generate embedding
    embedding = get_embedding(query_text)
    if not embedding:
        print("ERROR: No embedding vector returned from Ollama")
        return []

    # Query Qdrant
    try:
        response = client.query_points(
            collection_name=collection,
            query=embedding,
            limit=top_k,
            with_payload=True
        )
    except Exception as e:
        print(f"ERROR: Qdrant query failed for collection '{collection}'")
        print(f"Details: {e}")
        return []

    results = response.points or []
    elapsed = round(time.time() - start_time, 3)

    # Format results
    formatted = [
        {
            "rank": i + 1,
            "score": round(r.score, 4),
            "filename": r.payload.get("filename", "unknown"),
            "content": r.payload.get("content", ""),
        }
        for i, r in enumerate(results)
    ]

    # Display results
    if not silent:
        print(f"\n{'='*70}")
        print(f"Agent: {agent_name.upper()} | Query: \"{query_text}\" | Time: {elapsed}s")
        print(f"{'='*70}")
        
        if not results:
            print("No results found.")
        else:
            for f in formatted:
                content_preview = f["content"][:200]
                if len(f["content"]) > 200:
                    content_preview += "..."
                
                print(f"\n[{f['rank']}] Score: {f['score']:.4f} | File: {f['filename']}")
                print(f"    {content_preview}")
        
        print(f"\n{'='*70}")
        print(f"Retrieved {len(results)}/{top_k} results from {collection}")
        print("Note: Score 1.0 = perfect match, 0.0 = unrelated")

    return formatted


def main():
    if len(sys.argv) < 3:
        print("Usage: python query_agent_memory.py <AGENT> <QUERY>")
        print("\nExamples:")
        print("  python query_agent_memory.py CEO \"Q1 revenue goals\"")
        print("  python query_agent_memory.py CFO \"financial planning\"")
        sys.exit(1)

    agent = sys.argv[1]
    query = " ".join(sys.argv[2:])
    query_agent(agent, query)



    main()

import json
import sys

if __name__ == "__main__":
    try:
        agent = sys.argv[1] if len(sys.argv) > 1 else None
        query = sys.argv[2] if len(sys.argv) > 2 else None
        if not agent or not query:
            raise ValueError("Usage: query_agent_memory.py <agent> <message>")

        # Simulate existing retrieval
        top_result = f"Processed query for agent: {agent} → {query}"

        # ✅ Return structured JSON for FastAPI
        print(json.dumps({
            "agent": agent,
            "response": top_result,
            "status": "ok"
        }))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
