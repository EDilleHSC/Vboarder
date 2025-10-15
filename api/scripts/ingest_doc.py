import hashlib
import sys
from pathlib import Path
from time import time

from docling.document_converter import DocumentConverter
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, PointStruct, VectorParams

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
VECTOR_SIZE = 768  # embeddinggemma:300m dimension

converter = DocumentConverter()


def get_embedding(text: str):
    from embedding import get_embedding

    return get_embedding(text)


def ensure_collection(client: QdrantClient, collection: str):
    """Create collection if it doesn't exist"""
    try:
        client.get_collection(collection)
    except UnexpectedResponse:
        print(f"Creating collection: {collection}")
        client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )


def generate_doc_id(agent: str, filename: str) -> str:
    """Generate consistent ID from agent + filename to prevent duplicates"""
    content = f"{agent.lower()}:{filename}"
    return hashlib.md5(content.encode()).hexdigest()


def document_exists(client: QdrantClient, collection: str, doc_id: str) -> bool:
    """Check if document already ingested"""
    try:
        result = client.retrieve(collection_name=collection, ids=[doc_id])
        return len(result) > 0
    except:
        return False


def extract_text(p: Path) -> str:
    """Extract text from document with fallback"""
    if p.suffix.lower() in [".pdf", ".md"]:
        doc = converter.convert(str(p))

        try:
            return doc.document.export_to_markdown()
        except AttributeError:
            # Fallback: manual extraction
            markdown_parts = []
            if hasattr(doc.document, "pages"):
                for page in doc.document.pages:
                    if hasattr(page, "elements"):
                        for element in page.elements:
                            if hasattr(element, "text"):
                                markdown_parts.append(element.text)
            return "\n".join(markdown_parts) if markdown_parts else ""

    return p.read_text(encoding="utf-8", errors="ignore")


def ingest(
    agent: str, p: Path, client: QdrantClient, skip_duplicates: bool = True
) -> int:
    """Ingest single document with duplicate detection"""
    collection = f"agent_{agent.lower()}_memory"
    doc_id = generate_doc_id(agent, p.name)

    # Skip if already exists
    if skip_duplicates and document_exists(client, collection, doc_id):
        print(f"  [SKIP] {p.name} (already ingested)")
        return 0

    try:
        text = extract_text(p)
    except Exception as e:
        print(f"  [ERROR] Failed to read {p.name}: {e}")
        return 0

    if not text.strip():
        print(f"  [SKIP] {p.name} (empty content)")
        return 0

    try:
        vector = get_embedding(text)
    except Exception as e:
        print(f"  [ERROR] Failed to generate embedding for {p.name}: {e}")
        return 0

    point = PointStruct(
        id=doc_id,  # Consistent ID prevents duplicates
        payload={"agent": agent, "filename": p.name, "content": text},
        vector=vector,
    )

    try:
        client.upsert(collection_name=collection, points=[point])
        print(f"  [OK] {p.name}")
        return 1
    except Exception as e:
        print(f"  [ERROR] Failed to upsert {p.name}: {e}")
        return 0


def ingest_multiple(agent: str, path: str, skip_duplicates: bool = True):
    """Ingest multiple documents with progress tracking"""
    p = Path(path)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    collection = f"agent_{agent.lower()}_memory"

    # Ensure collection exists
    ensure_collection(client, collection)

    count = 0
    skipped = 0
    errors = 0
    start = time()

    # Gather files
    if p.is_dir():
        files = [f for f in p.rglob("*") if f.suffix.lower() in [".txt", ".pdf", ".md"]]
    elif p.is_file():
        files = [p] if p.suffix.lower() in [".txt", ".pdf", ".md"] else []
    else:
        print(f"ERROR: Path does not exist: {path}")
        return

    if not files:
        print(f"No documents found in {path}")
        return

    print(f"\nIngesting {len(files)} file(s) for agent {agent.upper()}")
    print(f"Collection: {collection}")
    print(f"Duplicate detection: {'ON' if skip_duplicates else 'OFF'}\n")

    # Process files
    for i, file in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Processing {file.name}...")
        result = ingest(agent, file, client, skip_duplicates)
        if result == 1:
            count += 1
        elif result == 0 and skip_duplicates:
            # Check if it was skipped vs error by looking at output
            skipped += 1

    elapsed = time() - start

    # Summary
    print(f"\n{'='*60}")
    print(f"Ingestion Summary for {agent.upper()}")
    print(f"{'='*60}")
    print(f"Ingested: {count} files")
    print(f"Skipped: {skipped - count} files (duplicates)")
    print(f"Errors: {errors} files")
    print(f"Time: {elapsed:.2f}s")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ingest_doc.py <agent> <path> [--force]")
        print("\nOptions:")
        print("  --force    Re-ingest documents even if they already exist")
        print("\nExamples:")
        print("  python ingest_doc.py CEO /path/to/docs")
        print("  python ingest_doc.py CFO /path/to/docs --force")
        sys.exit(1)

    agent = sys.argv[1]
    path = sys.argv[2]
    skip_duplicates = "--force" not in sys.argv

    ingest_multiple(agent, path, skip_duplicates)
