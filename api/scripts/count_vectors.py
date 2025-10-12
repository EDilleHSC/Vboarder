from qdrant_client import QdrantClient
c = QdrantClient('localhost', 6333)
print(f"CEO memory: {c.count('agent_ceo_memory').count} vectors")
print(f"CFO memory: {c.count('agent_cfo_memory').count} vectors")
