# PDF Chat (RAG)

[![CI](https://img.shields.io/github/actions/workflow/status/Praansu/pdf-chat-rag/ci.yml?style=flat-square)](https://github.com/Praansu/pdf-chat-rag/actions)
[![License](https://img.shields.io/badge/License-MIT-1F2328?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-1F2328?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-1F2328?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-ready-1F2328?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

Upload a PDF, ask questions about it. Built this because I kept re-reading long PDFs for class.

**PyMuPDF** pulls the text, **sentence-transformers + ChromaDB** find the relevant bits, **Groq Llama 3** writes the answer. Streaming + you can delete docs without restarting.

## Quick Start

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Add your Groq API key
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# 3. Run
python app.py  # Streamlit, opens in browser
```

Or with Docker:
```bash
docker build -t pdf-chat-rag .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key pdf-chat-rag
```

PDFs go in `uploads/`. Streamlit UI at `http://localhost:8000`.

## Stack

| Layer | Tech |
|-------|------|
| PDF Parsing | PyMuPDF (fitz) |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| LLM | Groq (Llama 3 8B) |
| Frontend | Streamlit |
| API | FastAPI + SSE streaming |

## Features

- Upload PDF → auto-chunk → embed → store in ChromaDB
- Ask questions → RAG retrieval → streaming answer
- Delete documents without restart
- Document management UI

## Known Limitations

- **Scanned PDFs don't work** — no OCR yet (Tesseract/pytesseract planned)
- Large PDFs are slow — need better chunking strategy
- Single-user (no auth)

## What I Learned

- Streaming responses via SSE feels much faster than waiting for full generation
- ChromaDB is simple but lacks advanced filtering
- Chunk size / overlap dramatically affects retrieval quality
- Deleting vectors by ID in ChromaDB requires manual collection management