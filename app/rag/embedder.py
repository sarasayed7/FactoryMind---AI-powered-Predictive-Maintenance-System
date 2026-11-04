from sentence_transformers import SentenceTransformer
from app.rag.chunker import chunks

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def embed_chunks(chunks):
    # 1. Extract text from each chunk
    texts = [chunk["text"] for chunk in chunks]

    # 2. Generate embeddings using model.encode()
    embedding = model.encode(texts)

    # 3. Return the embeddings
    return embedding

# test
embeddings = embed_chunks(chunks)

print("Number of chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)
