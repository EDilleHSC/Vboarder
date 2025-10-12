import os
import json
import asyncpg
import openai
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, PointStruct

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # e.g. postgresql://user:pass@localhost:5432/vboarder
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
openai.api_key = os.getenv("OPENAI_API_KEY")

# Map agent -> qdrant collection name
def agent_collection(agent: str) -> str:
    return f"agent_{agent.lower()}_memory"

async def init_db_pool():
    return await asyncpg.create_pool(
        DATABASE_URL,
        min_size=2,
        max_size=10,
        command_timeout=60,
    )

def get_qdrant():
    return QdrantClient(url=QDRANT_URL)

async def embed_text(text: str):
    # Swap with Ollama if desired
    resp = await openai.embeddings.create(model=EMBED_MODEL, input=text)
    return resp.data[0].embedding

async def search_knowledge_base(pool, agent: str, query: str, top_k: int = 5):
    """
    RAG retrieval:
    - Embed query
    - Search Qdrant in the agent's collection
    - Fetch pretty doc names from Postgres for display
    """
    vector = await embed_text(query)
    collection = agent_collection(agent)

    qdrant = get_qdrant()
    hits = qdrant.search(
        collection_name=collection,
        query_vector=vector,
        limit=top_k,
    )

    if not hits:
        return ""

    # Build result strings; payload expected: {document_id, doc_name, content, chunk_seq}
    contexts = []
    doc_ids = set()
    for h in hits:
        p = h.payload or {}
        snippet = p.get("content", "")
        doc_name = p.get("doc_name") or "Unknown Source"
        contexts.append(f"Source: {doc_name}\n{snippet[:800]}...")
        if "document_id" in p:
            doc_ids.add(p["document_id"])

    results = "\n\n".join(contexts)
    return f"=== Retrieved Knowledge Chunks ===\n{results}\n\nUse this information as background context."