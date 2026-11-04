from pathlib import Path
import pymupdf

def load_manual(pdf_path: str):
    pages= []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text('text')

            if not text.strip():
                continue

            page_data = {
                "source" : Path(pdf_path).name,
                "page_number": page_number,
                "text": text.strip()
            }

            pages.append(page_data)

    return pages


# Test
pages = load_manual("data/manuals/machine_manual.pdf")

print("Pages extracted:", len(pages))
print("First page:", pages[0]["page_number"])
print("Text preview:", pages[0]["text"][:200])