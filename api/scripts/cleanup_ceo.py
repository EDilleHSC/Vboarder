from qdrant_client import QdrantClient

c = QdrantClient(host='localhost', port=6333)

print('Deleting CEO collection...')
c.delete_collection('agent_ceo_memory')
print('Done. Re-run ingestion to recreate with 2 vectors.')
