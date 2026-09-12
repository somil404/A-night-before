# 📚 The Night Before

### AI-Powered Study Assistant for Course Materials

**The Night Before** is a document-grounded AI study assistant that helps students revise from their own course material.

Instead of answering from general AI knowledge, the system first searches the uploaded study material, retrieves the most relevant sections, and then uses Gemini to generate an answer based only on those sections.

If the required information is not present in the provided material, the assistant refuses to answer rather than hallucinating.

---

## 🎯 Problem

Students often have multiple sources of study material:

* Lecture PDFs
* Presentation slides
* Text/Markdown notes
* Scanned notes
* Handwritten notes
* Diagrams, tables and equations

Finding the correct information across all these materials before an exam can be time-consuming.

**The Night Before** provides a single interface where students can upload their study material and ask questions naturally.

---

## ✨ Features

* 📄 Upload PDF, TXT and Markdown files
* 🖼️ Upload image-based notes
* ✍️ OCR support for scanned/handwritten notes
* 🔍 Semantic search using embeddings
* 🧠 Retrieval-Augmented Generation (RAG)
* 🤖 Gemini-powered answer generation
* 📖 Source and page citations
* 🛑 Refuses questions not covered by the provided material
* 💻 Simple Streamlit interface
* 🔒 Answers are grounded in the uploaded material instead of relying on general knowledge

---

## 🔄 How It Works

```text
                Upload Study Material
                         │
                         ▼
              Text Extraction / OCR
                         │
                         ▼
                    Chunking
                         │
                         ▼
                  Embeddings
                         │
                         ▼
                    ChromaDB
                         │
                         │
                  Student Question
                         │
                         ▼
                Question Embedding
                         │
                         ▼
             Semantic Similarity Search
                         │
                         ▼
                Relevant Context
                         │
                         ▼
                    Gemini
                         │
                         ▼
              Grounded Answer + Citation
```

### RAG Pipeline

The system follows a simple **Retrieval-Augmented Generation (RAG)** approach:

1. The student uploads a document.
2. Text is extracted from the document.
3. Images are processed using OCR.
4. The extracted content is divided into smaller chunks.
5. Each chunk is converted into an embedding using Sentence Transformers.
6. The embeddings are stored in ChromaDB.
7. When a question is asked, the question is also converted into an embedding.
8. ChromaDB retrieves the most relevant sections.
9. The retrieved sections are provided to Gemini.
10. Gemini generates an answer using only the retrieved study material.
11. The application displays the source document and page number.

---

## 🛑 Hallucination Prevention

A major goal of the project is to prevent the AI from answering questions that are not supported by the study material.

The prompt explicitly instructs the model:

```text
Do not use outside knowledge.
Do not guess.
Do not invent facts.
Do not invent page numbers.
```

If the required information cannot be found in the uploaded material, the assistant responds:

> "This information is not covered in the provided study material."

This makes the system behave more like an **open-book study assistant** rather than a general-purpose chatbot.

---

## 📖 Source Citations

Each document chunk is stored together with metadata such as:

```text
Source: Nature and Scope of Economics.pdf
Page: 2
```

When relevant content is retrieved, the answer can identify where the information came from.

Example:

```text
Answer:
Normative economics deals with statements about what ought to be
or what should happen.

Source:
Nature and Scope of Economics.pdf — Page 2
```

This allows the student to verify the answer directly from their notes.

---

## 🛠️ Tech Stack

| Technology            | Purpose                           |
| --------------------- | --------------------------------- |
| Python                | Core application                  |
| Streamlit             | User interface                    |
| Gemini                | Answer generation                 |
| ChromaDB              | Vector database                   |
| Sentence Transformers | Text embeddings                   |
| PyMuPDF               | PDF text extraction               |
| Tesseract OCR         | Image/handwritten text extraction |
| Pillow                | Image processing                  |
| python-dotenv         | API key management                |

---

## 📁 Project Structure

```text
night-before/
│
├── documents/
│   └── study materials
│
├── chroma_db/
│   └── vector database
│
├── app.py
│   └── Streamlit application
│
├── ingest.py
│   └── Document ingestion
│
├── rag.py
│   └── RAG retrieval and generation
│
├── ocr_ingest.py
│   └── OCR processing for images
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd night-before
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

**Do not commit `.env` to GitHub.**

Your `.gitignore` should contain:

```gitignore
.env
venv/
__pycache__/
chroma_db/
```

---

## ▶️ Running the Application

Start the Streamlit application:

```bash
streamlit run app.py
```

The terminal will provide a local URL, usually:

```text
http://localhost:8501
```

Open it in your browser.

### Usage

1. Upload your study material.
2. Wait for the document to be processed.
3. Enter a question.
4. Click **Ask**.
5. The system retrieves relevant content.
6. Gemini generates a grounded answer.
7. The source document and page are displayed.

---

## 📂 Supported Files

The current application supports:

```text
PDF
TXT
Markdown
PNG
JPG
JPEG
```

PDF files can contain multiple pages, while image files are processed using OCR.

---

## ✍️ Handwritten Notes

The project includes OCR support for image-based notes.

The intended workflow is:

```text
Handwritten Note
       ↓
      OCR
       ↓
Extracted Text
       ↓
Chunking
       ↓
Embedding
       ↓
ChromaDB
       ↓
Question
       ↓
Answer + Source
```

OCR quality depends on the handwriting, image quality, lighting and scan clarity.

Very difficult handwriting may not be extracted accurately.

---

## ⚠️ Mocked / Demo Components

This project was designed as a fast competition prototype rather than a production application.

The following components are intentionally simplified:

* No authentication or user account system.
* No external HRMS/LMS/course database.
* Study materials are supplied by the user during the demo.
* Tesseract is used as the OCR engine and may have limited accuracy on difficult handwriting.
* ChromaDB is used locally rather than through a production vector database.
* The application runs locally through Streamlit.
* No production-scale document processing pipeline is implemented.

The core document retrieval, embeddings, vector search, RAG generation and refusal mechanism are implemented rather than mocked.

---

## 🧪 Testing Approach

The system can be tested using three categories of questions.

### 1. Questions Answerable from One Document

Example:

```text
What is normative economics?
```

Expected result:

```text
Correct answer + source + page number
```

### 2. Questions Requiring Multiple Documents

Questions can be designed so that relevant information must be retrieved from two or more uploaded study materials.

Expected result:

```text
Combined answer + relevant sources/pages
```

### 3. Questions Not Covered by the Material

Example:

```text
Who won the FIFA World Cup in 2022?
```

If this information does not exist in the uploaded study material, the system should refuse to answer.

Expected result:

```text
This information is not covered in the provided study material.
```

---

## 🎯 Competition Goal

The main objective of **The Night Before** is simple:

> **Your notes are the source of truth. Ask naturally, get grounded answers, and know exactly where the answer came from.**

The project focuses on three important properties:

**Groundedness** — answers come from the provided material.

**Traceability** — answers point back to the source document and page.

**Refusal** — the assistant does not invent an answer when the information is unavailable.

---

## 🔮 Future Improvements

Possible improvements for a production version include:

* Better handwriting OCR using a dedicated document AI model
* Improved table and equation extraction
* Multi-document querying in the main UI
* Better page-level citations
* Document preview alongside answers
* Conversation history
* User authentication
* Cloud-hosted vector database
* Background document ingestion
* Hybrid keyword + semantic search
* Reranking retrieved documents
* Evaluation dashboard for RAG accuracy

---

## 👨‍💻 Development

The project was developed incrementally, with separate commits for major components such as:

```text
Initialize study assistant project
Add document ingestion and text extraction
Implement semantic search with ChromaDB
Add Gemini grounded answer generation
Add OCR support for image notes
Add Streamlit document upload interface
Polish demo and update README
```

The Git history reflects the development process rather than a single final submission commit.

---

## 📜 License

This project is created as a prototype for an AI development competition.
