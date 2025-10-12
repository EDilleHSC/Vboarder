import time
import os
from docling import convert_documents

def check_ingestion_health():
    start = time.time()
    path = "example_docs"
    try:
        result = convert_documents(path)
        durations = [doc.document.metadata['duration'] for doc in result.documents]
        return {
            "status": "success",
            "file_count": len(result.documents),
            "avg_duration": round(sum(durations)/len(durations), 2),
            "formats": [doc.document.metadata['format'] for doc in result.documents]
        }
    except Exception as e:
        return {"status": "failure", "error": str(e)}
