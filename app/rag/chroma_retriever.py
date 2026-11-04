from app.rag.vector_store import collection
from app.rag.embedder import model

def retrieve_from_chroma(query, model, top_k=3, min_score = 0.30):
    query_embedding = model.encode([query])

    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Extract returned documents, metadata, and distances
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    # Convert them into a list of dictionaries
    retrieved_chunks = []

    for document, metadata, distance in zip(documents, metadatas, distances):
        similarity = 1 - distance
        if similarity < min_score:
            continue

        retrieve_chunks = {
            'source': metadata['source'],
            'page_number': metadata['page_number'],
            'chunk_id':  metadata["chunk_id"],
            'text':  document,
            'similarity_score': float(similarity)
            }

        retrieved_chunks.append(retrieve_chunks)


    # Return the retrieved chunks
    return retrieved_chunks

# test
results = retrieve_from_chroma(
    query="What routine maintenance is recommended?",
    model=model,
    top_k=3
)

for result in results:
    print("Source:", result["source"])
    print("Page:", result["page_number"])
    print("Similarity:", round(result["similarity_score"], 3))
    print("Text:", result["text"][:200])
    print("---")