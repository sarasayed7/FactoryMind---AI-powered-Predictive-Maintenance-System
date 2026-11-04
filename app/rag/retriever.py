from sklearn.metrics.pairwise import cosine_similarity
from app.rag.answer_generator import build_context, generate_answer
import numpy as np

from app.rag.chunker import chunks
from app.rag.embedder import embeddings, model

def retrieve_chunks(query, chunks, embeddings, model, top_k=3, min_score = 0.30):
    query_embedding = model.encode([query])

    scores = cosine_similarity(query_embedding, embeddings)[0]

    # 1. Find the indices of the highest scores.
    top_indices = np.argsort(scores)[::-1][:top_k] #--> reverse and retrieve top 3 highest scores

    results =[]

    # 2. Retrieve the corresponding chunks.
    for index in top_indices:
        chunk = chunks[index]
        score = float(scores[index])

        # Skip chunks with similarity below min_score
        if score < min_score:
            continue

        # Keep your existing result-building logic

        result = {
            'source': chunk['source'],
            'page_number': chunk['page_number'],
            'chunk_id': chunk['chunk_id'],
            'text': chunk['text'],
            'similarity_score': score
        }

        results.append(result)

    # 3. Return each chunk with its similarity score.
    return results

# test
questions = [
    # "What should I check if the servo motor overheats?",
    "What routine maintenance is recommended?",
    "What hydraulic oil pressure should I use?" #--> checkin min-score threshold
    # "What is the recommended hydraulic oil pressure for this servo system?" #--> not in the manual (checking hallucination)
]
for question in questions:
    results = retrieve_chunks(
    query=question,
    chunks=chunks,
    embeddings=embeddings,
    model=model,
    top_k=3
    )   
    # testing min_score
    print("\nQuestion:", question)
    print("Retrieved chunks:", len(results))
    print("Similarity scores:", [
        round(r["similarity_score"], 3) for r in results
    ])

# for i, result in enumerate(results, start=1):
#     print(f"\n--- Result {i} ---")
#     print("Source:", result["source"])
#     print("Page:", result["page_number"])
#     print("Score:", round(result["similarity_score"], 3))
#     print(result["text"])

# testing build_context from answer_generator
# context = build_context(results)
# print(context)

# testing generate_answer using LLM from answer_generator
# answer = generate_answer(
#     question=question,
#     retrieved_chunks=results
# )
# print(answer)