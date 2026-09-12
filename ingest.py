import fitz
import chromadb
from sentence_transformers import SentenceTransformer

# -----------------------------
# 1. Read PDF
# -----------------------------

pdf_path = "documents/Nature and Scope of Economics.pdf"

doc = fitz.open(pdf_path)

all_chunks = []
all_metadata = []

for page_number, page in enumerate(doc):

    text = page.get_text()

    if not text.strip():
        continue

    # Simple chunking
    chunk_size = 800

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size].strip()

        if chunk:
            all_chunks.append(chunk)

            all_metadata.append({
                "source": "Nature and Scope of Economics.pdf",
                "page": page_number + 1
            })


print("Total chunks:", len(all_chunks))


# -----------------------------
# 2. Create Embeddings
# -----------------------------

model = SentenceTransformer("all-MiniLM-L6-v2")

embeddings = model.encode(all_chunks)

print("Embeddings created!")


# -----------------------------
# 3. Store in ChromaDB
# -----------------------------

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_or_create_collection(
    name="study_material"
)

collection.add(
    ids=[str(i) for i in range(len(all_chunks))],
    documents=all_chunks,
    embeddings=embeddings.tolist(),
    metadatas=all_metadata
)

print("Stored in ChromaDB!")

print("Done!")