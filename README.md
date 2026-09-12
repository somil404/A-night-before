# 📚 The Night Before

### AI-Powered Study Assistant

**The Night Before** is a RAG-based AI study assistant that lets students upload their course materials and ask questions directly from them.

Instead of relying on general AI knowledge, the system retrieves relevant content from the uploaded documents and generates **grounded answers with source and page citations**.

If the information is not present in the study material, the assistant **refuses to answer** instead of hallucinating.

## ✨ Features

* 📄 Upload PDF, TXT, Markdown and image files
* 🔍 Semantic search using embeddings
* 🧠 RAG-powered answers using Gemini
* 📖 Source & page citations
* 🛑 Refuses questions not covered by the documents
* ✍️ OCR support for scanned/handwritten material
* 💻 Simple Streamlit interface

## 🛠️ Tech Stack

**Python · Streamlit · Gemini · ChromaDB · Sentence Transformers · PyMuPDF · Tesseract OCR**

## 🔄 How It Works

```text
Upload Document
      ↓
Text Extraction / OCR
      ↓
Chunking + Embeddings
      ↓
ChromaDB
      ↓
User Question
      ↓
Semantic Retrieval
      ↓
Gemini
      ↓
Answer + Source Citation
```

## 🚀 Run Locally

```bash
pip install -r requirements.txt
```

Create `.env`:

```env
GEMINI_API_KEY=your_api_key_here
```

Run:

```bash
streamlit run app.py
```

## 🎯 Goal

> **Your notes are the source of truth. Ask naturally, get grounded answers, and know exactly where the answer came from.**
