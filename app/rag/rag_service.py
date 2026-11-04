from sentence_transformers import SentenceTransformer

from app.rag.answer_generator import generate_answer
from app.rag.chroma_retriever import retrieve_from_chroma

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"

)

def answer_maintenance_question(question: str):
    # 1. Retrieve relevant passages from ChromaDB
    retrieved_chunks = retrieve_from_chroma(query=question, model=embedding_model, top_k=3)

    # 2. Check whether evidence was retrieved
    if not retrieved_chunks:
        return {
            "answer": "No relevant maintenance information found.",
            "sources": []
        }

    # 3. Send the question and passages to Gemini
    answer = generate_answer(question=question, retrieved_chunks=retrieved_chunks)

    # 4. prepare source metadata
    sources = [
            {
                'source': chunk['source'],
                'page_number': chunk['page_number'],
                'similarity_score': chunk['similarity_score']
            }
            for chunk in retrieved_chunks
        ]

    # 4. Return the answer
    return{
        'answer': answer,
        'sources': sources
    }

# Test
result = answer_maintenance_question(
    # "What routine maintenance is recommended?"
    "What hydraulic oil pressure should I use?" #--> testing outsider question
)

print("ANSWER:")
print(result["answer"])

print("\nSOURCES:")
for source in result["sources"]:
    print(source)