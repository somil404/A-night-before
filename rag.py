import os
import chromadb
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# -----------------------------------
# 1. Load embedding model
# -----------------------------------

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# -----------------------------------
# 2. Connect to ChromaDB
# -----------------------------------

chroma_client = chromadb.PersistentClient(path="./chroma_db")

collection = chroma_client.get_collection(
    name="study_material"
)


# -----------------------------------
# 3. Connect to Gemini
# -----------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env file")
    exit()

gemini_client = genai.Client(
    api_key=api_key
)


# -----------------------------------
# 4. Take question from user
# -----------------------------------

question = input("\nAsk a question: ")


# -----------------------------------
# 5. Convert question into embedding
# -----------------------------------

question_embedding = embedding_model.encode(
    question
).tolist()


# -----------------------------------
# 6. Search ChromaDB
# -----------------------------------

results = collection.query(
    query_embeddings=[question_embedding],
    n_results=5
)


# -----------------------------------
# 7. Prepare retrieved context
# -----------------------------------

context = ""

for i in range(len(results["documents"][0])):

    document = results["documents"][0][i]
    metadata = results["metadatas"][0][i]

    context += f"""
SOURCE: {metadata['source']}
PAGE: {metadata['page']}

CONTENT:
{document}

-----------------------------------
"""


# -----------------------------------
# 8. Create prompt for Gemini
# -----------------------------------

prompt = f"""
You are an AI study assistant.

Your job is to answer the student's question using ONLY
the study material provided below.

IMPORTANT RULES:

1. Use only the provided study material.
2. Do NOT use your general knowledge.
3. Do NOT make up information.
4. If the answer is not present in the provided material,
   respond exactly:

"This information is not covered in the provided study material."

5. Give a clear and simple answer.
6. At the end of the answer, provide the source file and page number.
7. Use the page number provided in the SOURCE/PAGE information.
8. Never invent a page number.
9. If multiple pages are used, mention all relevant pages.

STUDENT QUESTION:
{question}

STUDY MATERIAL:
{context}
"""


# -----------------------------------
# 9. Ask Gemini
# -----------------------------------

response = gemini_client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)


# -----------------------------------
# 10. Display answer
# -----------------------------------

print("\n========================================")
print("ANSWER")
print("========================================\n")

print(response.text)

print("\n========================================")