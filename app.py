import os
import io
import hashlib

import streamlit as st
import chromadb
import pymupdf
import pytesseract

from PIL import Image
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv


# ==========================================
# 1. Load API key
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in .env file")
    st.stop()


# ==========================================
# 2. Page configuration
# ==========================================

st.set_page_config(
    page_title="The Night Before",
    page_icon="📚",
    layout="wide"
)


# ==========================================
# 3. Load models
# ==========================================

@st.cache_resource
def load_models():

    embedding_model = SentenceTransformer(
        "all-MiniLM-L6-v2"
    )

    gemini_client = genai.Client(
        api_key=api_key
    )

    return embedding_model, gemini_client


embedding_model, gemini_client = load_models()


# ==========================================
# 4. ChromaDB
# ==========================================

chroma_client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = chroma_client.get_or_create_collection(
    name="uploaded_documents"
)


# ==========================================
# 5. Extract PDF text
# ==========================================

def extract_pdf(file_bytes, file_name):

    document = pymupdf.open(
        stream=file_bytes,
        filetype="pdf"
    )

    chunks = []

    for page_number, page in enumerate(document):

        text = page.get_text().strip()

        if not text:
            continue

        # Split large pages into smaller chunks
        chunk_size = 1000

        for start in range(
            0,
            len(text),
            chunk_size
        ):

            chunk = text[
                start:start + chunk_size
            ]

            chunks.append({
                "text": chunk,
                "source": file_name,
                "page": page_number + 1
            })

    return chunks


# ==========================================
# 6. Extract TXT / MD
# ==========================================

def extract_text(file_bytes, file_name):

    text = file_bytes.decode(
        "utf-8",
        errors="ignore"
    )

    chunks = []

    chunk_size = 1000

    for start in range(
        0,
        len(text),
        chunk_size
    ):

        chunk = text[
            start:start + chunk_size
        ]

        chunks.append({
            "text": chunk,
            "source": file_name,
            "page": 1
        })

    return chunks


# ==========================================
# 7. Extract image text
# ==========================================

def extract_image(file_bytes, file_name):

    image = Image.open(
        io.BytesIO(file_bytes)
    )

    text = pytesseract.image_to_string(
        image
    ).strip()

    if not text:
        return []

    chunks = []

    chunk_size = 1000

    for start in range(
        0,
        len(text),
        chunk_size
    ):

        chunk = text[
            start:start + chunk_size
        ]

        chunks.append({
            "text": chunk,
            "source": file_name,
            "page": 1
        })

    return chunks


# ==========================================
# 8. Process uploaded file
# ==========================================

def process_file(uploaded_file):

    file_bytes = uploaded_file.getvalue()

    file_name = uploaded_file.name

    extension = file_name.lower().split(".")[-1]

    if extension == "pdf":

        chunks = extract_pdf(
            file_bytes,
            file_name
        )

    elif extension in ["txt", "md"]:

        chunks = extract_text(
            file_bytes,
            file_name
        )

    elif extension in ["png", "jpg", "jpeg"]:

        chunks = extract_image(
            file_bytes,
            file_name
        )

    else:

        return []


    # Create a unique ID for this upload
    file_hash = hashlib.md5(
        file_bytes
    ).hexdigest()[:10]


    # Add chunks to ChromaDB
    for index, item in enumerate(chunks):

        chunk_id = (
            f"{file_hash}_{index}"
        )

        embedding = embedding_model.encode(
            item["text"]
        ).tolist()

        collection.upsert(

            ids=[
                chunk_id
            ],

            embeddings=[
                embedding
            ],

            documents=[
                item["text"]
            ],

            metadatas=[
                {
                    "source": item["source"],
                    "page": item["page"]
                }
            ]
        )


    return chunks


# ==========================================
# 9. UI
# ==========================================

st.title("📚 The Night Before")

st.write(
    "Upload your study material and ask questions from it."
)

st.divider()


# ==========================================
# 10. Upload
# ==========================================

uploaded_file = st.file_uploader(
    "📂 Upload your study document",
    type=[
        "pdf",
        "txt",
        "md",
        "png",
        "jpg",
        "jpeg"
    ]
)


# ==========================================
# 11. Process upload
# ==========================================

if uploaded_file:

    file_id = (
        uploaded_file.name
        + str(uploaded_file.size)
    )

    if st.session_state.get(
        "processed_file"
    ) != file_id:

        with st.spinner(
            "Reading your document..."
        ):

            chunks = process_file(
                uploaded_file
            )

        st.session_state[
            "processed_file"
        ] = file_id

        st.session_state[
            "document_chunks"
        ] = chunks

    else:

        chunks = st.session_state.get(
            "document_chunks",
            []
        )


    if len(chunks) > 0:

        st.success(
            f"✅ {uploaded_file.name} processed successfully!"
        )

        st.info(
            f"Found {len(chunks)} searchable sections."
        )

    else:

        st.error(
            "Could not extract text from this file."
        )
        
# ==========================================
# 12. Question
# ==========================================

if uploaded_file:

    st.divider()

    st.subheader(
        "💬 Ask about your document"
    )

    question = st.text_input(
        "Your question",
        placeholder="e.g. What is normative economics?"
    )


    # ======================================
    # 13. Ask question
    # ======================================

    if st.button(
        "Ask",
        type="primary"
    ):

        if not question.strip():

            st.warning(
                "Please enter a question."
            )

        else:

            # ------------------------------
            # Question embedding
            # ------------------------------

            question_embedding = (
                embedding_model
                .encode(question)
                .tolist()
            )


            # ------------------------------
            # Search document
            # ------------------------------

            results = collection.query(

                query_embeddings=[
                    question_embedding
                ],

                n_results=5
            )


            # ------------------------------
            # Build context
            # ------------------------------

            context = ""

            sources = []

            for i in range(
                len(results["documents"][0])
            ):

                document = (
                    results["documents"][0][i]
                )

                metadata = (
                    results["metadatas"][0][i]
                )

                source = metadata.get(
                    "source",
                    "Unknown"
                )

                page = metadata.get(
                    "page",
                    "Unknown"
                )

                # IMPORTANT:
                # Only use the currently
                # uploaded document

                if source != uploaded_file.name:
                    continue

                context += f"""

SOURCE: {source}
PAGE: {page}

CONTENT:
{document}

-----------------------------
"""

                sources.append(
                    f"{source} — Page {page}"
                )


            # ------------------------------
            # Gemini prompt
            # ------------------------------

            prompt = f"""
You are "The Night Before",
an AI study assistant.

Answer the student's question ONLY
using the document content provided below.

STRICT RULES:

1. Do not use outside knowledge.
2. Do not use your own knowledge.
3. Do not guess.
4. Do not invent facts.
5. Do not invent page numbers.
6. If the answer is not present in the
   document, respond exactly:

"This information is not covered in
the provided study material."

7. Give a simple and clear explanation.
8. At the end, mention the exact source
   file and page number.
9. If multiple pages are used, mention
   all relevant pages.

QUESTION:

{question}

DOCUMENT CONTENT:

{context}
"""


            # ------------------------------
            # Generate answer
            # ------------------------------

            with st.spinner(
                "Thinking..."
            ):

                response = (
                    gemini_client
                    .models
                    .generate_content(
                        model="gemini-3.6-flash",
                        contents=prompt
                    )
                )


            # ------------------------------
            # Display answer
            # ------------------------------

            st.divider()

            st.subheader(
                "🤖 Answer"
            )

            st.write(
                response.text
            )


            # ------------------------------
            # Sources
            # ------------------------------

            st.subheader(
                "📖 Sources"
            )

            unique_sources = list(
                dict.fromkeys(sources)
            )

            for source in unique_sources:

                st.write(
                    "• " + source
                )