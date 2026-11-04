import chromadb
from pathlib import Path

from app.rag.chunker import chunks
from app.rag.embedder import embeddings

DB_PATH = Path(__file__).resolve().parents[2] / "chroma_db"

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

collection = client.get_or_create_collection(
    name="factorymind_maintenance",
    configuration={"hnsw": {"space": "cosine"}},
    embedding_function=None
)

# print("Stored chunks:", collection.count())  #--> before --> 0

def store_chunks(chunks, embeddings):
    # 1. Extract unique IDs
    ids = [
    f"{chunk['source']}:{chunk['page_number']}:{chunk['chunk_id']}"
    for chunk in chunks]

    # 2. Extract document texts
    documents = []
    for chunk in chunks:
        document = chunk['text']

        documents.append(document)

    # 3. Extract metadata
    metadatas = []
    for chunk in chunks:
        metadata = {
        "source": chunk["source"],
        "page_number": chunk["page_number"],
        "chunk_id": chunk["chunk_id"]}

        metadatas.append(metadata)
    # 4. Store everything in Chroma
    if not chunks:
        return

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have matching lengths")
    
    collection.upsert(
    ids=ids,
    documents=documents,
    metadatas=metadatas,
    embeddings=embeddings.tolist()
    )

store_chunks(chunks, embeddings)

print("Stored chunks:", collection.count()) #--> after --> 55