# PDF Chat RAG

Upload a PDF, ask questions about it. The answers come from the document itself — not from the model's training data.

## Why I built this

I wanted to understand how RAG (Retrieval Augmented Generation) actually works under the hood. There are plenty of libraries that abstract it away, but I wanted to build each piece myself: parsing PDFs, chunking text, generating embeddings, storing vectors, retrieving relevant chunks, and feeding them to an LLM. That way when something breaks, I know exactly where to look.

## How it works

```
Upload PDF → Extract text → Split into chunks → Embed with sentence-transformers → Store in ChromaDB
                                                                                      ↓
You ask a question → Embed the question → Find 3 most similar chunks → Send chunks + question to Groq's Llama 3
                                                                                      ↓
                                                                                Answer with page citations
```

## Tech stack

- **Backend:** FastAPI (Python)
- **PDF parsing:** PyMuPDF (fitz)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2) — runs locally, no API key needed
- **Vector store:** ChromaDB (persistent, file-based)
- **LLM:** Groq API (Llama 3 70B) — free tier, fast
- **Frontend:** Plain HTML/CSS/JS — no framework, keeps it simple
- **Container:** Docker

## What I learned

- RAG is 80% chunking strategy, 20% LLM. I started with fixed-size chunks and kept getting irrelevant results. Switching to sentence-based chunking with overlap made a huge difference.
- sentence-transformers is surprisingly fast for a local model. The first load takes a few seconds to download, but subsequent loads are instant.
- ChromaDB's persistent client works well for this use case. I don't need a separate database server — it just writes to disk.
- Groq's Llama 3 70B is ridiculously fast. Almost feels like cheating compared to running models locally.

## What I'd improve

- **Chunking:** Still not perfect. Long documents with tables or code blocks need a smarter approach.
- **No auth:** Anyone can upload anything. Fine for a demo, not for production.
- **No file management:** Uploaded PDFs stay on disk. Should add cleanup or user-specific storage.
- **Streaming:** The LLM response comes all at once. Would be nicer to stream it token by token.
- **Better UI:** It works, but it's basic. Loading states could be smoother.

## Getting started

```bash
# Clone and install
git clone https://github.com/Praansu/pdf-chat-rag
cd pdf-chat-rag
pip install -r requirements.txt

# Set up your API key
cp .env.example .env
# Edit .env and add your Groq API key (get one free at https://console.groq.com)

# Run it
uvicorn backend.main:app --reload
```

Open http://localhost:8000, upload a PDF, and start asking questions.

### Docker

```bash
docker compose up --build
```

## API

| Endpoint | Method | What it does |
|----------|--------|-------------|
| `/upload` | POST | Upload a PDF, returns a doc_id |
| `/chat` | POST | Ask a question about the uploaded document |
| `/health` | GET | Health check |

## What I'd tell someone building something similar

Don't start with LangChain or LlamaIndex. Build the dumb version first — extract text, split into chunks, stuff it into a vector store, retrieve and ask. Once that works, you'll actually understand what the frameworks are doing for you.
