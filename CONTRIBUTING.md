# Contributing to PDF Chat RAG

Thank you for considering contributing!

## How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** with clear, focused commits
4. **Run tests and linting**: `ruff check backend/ && ruff format --check backend/`
5. **Open a Pull Request** with a clear description

## Code Style

- Python: ruff for linting and formatting
- Commit messages: Conventional Commits

## Development Setup

```bash
git clone https://github.com/Praansu/pdf-chat-rag.git
cd pdf-chat-rag
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn backend.main:app --reload
```

## Project Structure

```
pdf-chat-rag/
├── backend/
│   ├── main.py       # FastAPI endpoints (upload, chat, chat/stream, documents CRUD)
│   ├── embeddings.py # ChromaDB + sentence-transformers
│   ├── processor.py  # PDF extraction + chunking
│   └── llm.py        # Groq integration (streaming + non-streaming)
├── frontend/
│   └── index.html    # Vanilla JS chat UI with SSE streaming
└── .github/workflows/ # CI/CD pipelines
```

## Areas for Contribution

- Add PDF page citations inline in answers
- Improve chunking strategy (semantic chunking)
- Add authentication/multi-user support
- Write unit/integration tests
- Improve frontend UX
- Add Docker Compose for production