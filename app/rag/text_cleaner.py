import re
from app.rag.document_loader import load_manual

def clean_text(text:str) -> str:
    text = text.replace('\uFFFD', '')
    text = text.replace('\x08', '')
    text = "".join(
        char for char in text
        if char.isprintable() or char == "\n"
        )
    text = re.sub(r'[\t]+', ' ', text)

    return text

# test
pages = load_manual("data/manuals/machine_manual.pdf")

original = pages[0]["text"]
cleaned = clean_text(original)

print("Before:")
print(repr(original[:250]))

print("\nAfter:")
print(repr(cleaned[:250]))