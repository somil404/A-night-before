import os
import pytesseract
from PIL import Image
import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------------
# 1. Tesseract location
# -----------------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# -----------------------------------
# 2. Load embedding model
# -----------------------------------

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------------
# 3. Connect to ChromaDB
# -----------------------------------

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_collection(
    name="study_material"
)


# -----------------------------------
# 4. Handwritten notes folder
# -----------------------------------

folder = "documents/handwritten"

files = os.listdir(folder)

image_files = [
    file for file in files
    if file.lower().endswith(
        (".png", ".jpg", ".jpeg")
    )
]


# -----------------------------------
# 5. Process every handwritten page
# -----------------------------------

for file in image_files:

    image_path = os.path.join(folder, file)

    print("\nProcessing:", file)

    # Open image
    image = Image.open(image_path)

    # OCR
    text = pytesseract.image_to_string(
        image
    )

    # Remove unnecessary whitespace
    text = text.strip()

    print("\nOCR TEXT:")
    print(text)


    # -----------------------------------
    # Check if OCR found anything
    # -----------------------------------

    if not text:
        print("No text detected. Skipping...")
        continue


    # -----------------------------------
    # Split into chunks
    # -----------------------------------

    chunk_size = 800

    chunks = []

    for i in range(
        0,
        len(text),
        chunk_size
    ):

        chunk = text[
            i:i + chunk_size
        ]

        chunks.append(chunk)


    # -----------------------------------
    # Add chunks to ChromaDB
    # -----------------------------------

    for chunk_number, chunk in enumerate(chunks):

        embedding = embedding_model.encode(
            chunk
        ).tolist()

        collection.add(
            ids=[
                f"{file}_chunk_{chunk_number}"
            ],

            embeddings=[
                embedding
            ],

            documents=[
                chunk
            ],

            metadatas=[
                {
                    "source": file,
                    "page": 1,
                    "type": "handwritten"
                }
            ]
        )


print("\n===================================")
print("Handwritten notes added to ChromaDB")
print("===================================")