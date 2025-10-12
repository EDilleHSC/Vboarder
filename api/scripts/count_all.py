from qdrant_client import QdrantClient

c = QdrantClient(host='localhost', port=6333)

collections = ['agent_ceo_memory', 'agent_cfo_memory', 'agent_air_memory', 
               'agent_clo_memory', 'agent_cmo_memory', 'agent_coo_memory',
               'agent_cos_memory', 'agent_cto_memory', 'agent_sec_memory']

for coll in collections:
    try:
        count = c.count(coll).count
        print(f"{coll}: {count} vectors")
    except Exception as e:
        print(f"{coll}: ERROR - {e}")
