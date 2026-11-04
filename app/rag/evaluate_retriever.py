from app.rag.chunker import chunks
from app.rag.embedder import embeddings, model
from app.rag.retriever import retrieve_chunks

evaluation_cases = [
    {
        "question": "What should I check if the servo motor overheats?",
        "expected_pages": [3, 5]
    },
    {
        "question": "How should damaged cables and connections be inspected?",
        "expected_pages": [2]
    },
    {
        "question": "What routine maintenance is recommended?",
        "expected_pages": [2, 3]
    }
]

def evaluate_retrieval(chunks, embeddings, model):
    for case in evaluation_cases:
        results = retrieve_chunks(
            query=case["question"],
            chunks=chunks,
            embeddings=embeddings,
            model=model,
            top_k=3
        )

        print("\nQUESTION:", case["question"])
        print("Expected PDF pages:", case["expected_pages"])

        for rank, result in enumerate(results, start=1):
            print(f"\nRank {rank}")
            print("PDF page:", result["page_number"])
            print("Similarity:", round(result["similarity_score"], 3))
            print("Passage:", result["text"])

        retrieved_pages = {r["page_number"] for r in results}
        page_hit = bool(
            retrieved_pages.intersection(case["expected_pages"])
        )

        print("\nExpected-page hit:", page_hit)
        print("-" * 60)
evaluate_retrieval(chunks, embeddings, model)