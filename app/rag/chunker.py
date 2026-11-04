from app.rag.document_loader import load_manual
from app.rag.text_cleaner import clean_text

def chunk_pages(pages, chunk_size = 500, chunk_overlap = 100):

    if chunk_size <= 0 or not 0 <= chunk_overlap < chunk_size:
        raise ValueError("Invalid chunk size or overlap")

    chunks = []
    step = chunk_size - chunk_overlap

    for page in pages:
        text = clean_text(page['text'])
        chunk_id = 0

        for start in range(0, len(text), step):
            chunk_text = text[start:start + chunk_size]

            if not chunk_text.strip():
                continue

            chunk_data = {
                "source": page['source'],
                'page_number': page['page_number'],
                'chunk_id': chunk_id,
                'text': chunk_text
            }

            chunks.append(chunk_data)
            chunk_id += 1

    return chunks

# test
pages = load_manual("data/manuals/machine_manual.pdf")

chunks = chunk_pages(
    pages,
    chunk_size=500,
    chunk_overlap=100
)

print("Extracted pages:", len(pages))
print("Generated chunks:", len(chunks))
print("First chunk:", chunks[0])