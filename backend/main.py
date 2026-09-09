"""PDF Chat RAG — FastAPI backend."""

import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .embeddings import VectorStore
from .models import ChatRequest, ChatResponse, Source, UploadResponse, DeleteResponse
from .processor import chunk_text, extract_text

load_dotenv()

app = FastAPI(title="PDF Chat RAG", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Lazy-loaded vector store — first upload triggers model download
store: VectorStore | None = None


def get_store() -> VectorStore:
    global store
    if store is None:
        store = VectorStore()
    return store


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, "Only PDF files are allowed")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large — max 20MB")

    doc_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{doc_id}.pdf"
    save_path.write_bytes(content)

    # Extract + chunk + embed
    try:
        pages = extract_text(save_path)
        if not pages:
            raise HTTPException(400, "Could not extract any text from this PDF")

        chunks = chunk_text(pages)
        vs = get_store()
        chunk_count = vs.add_document(doc_id, chunks)
    except HTTPException:
        raise
    except Exception as e:
        # Clean up on failure
        save_path.unlink(missing_ok=True)
        raise HTTPException(500, f"Failed to process PDF: {str(e)}")

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename or "document.pdf",
        size=len(content),
        chunks=chunk_count,
        pages=len(pages),
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty")

    vs = get_store()
    results = vs.search(req.query, top_k=req.top_k or 3)

    if not results:
        return ChatResponse(
            answer="No relevant content found in the uploaded document.", sources=[]
        )

    context = "\n\n".join(f"[Page {r['page_num']}] {r['text']}" for r in results)

    # Import here to avoid circular dependency with models
    from .llm import ask_groq

    answer = ask_groq(req.query, context)

    return ChatResponse(
        answer=answer,
        sources=[
            Source(
                page_num=r["page_num"], text=r["text"][:200], score=round(r["score"], 3)
            )
            for r in results
        ],
    )


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """Stream chat response as SSE."""
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty")

    vs = get_store()
    results = vs.search(req.query, top_k=req.top_k or 3)

    if not results:

        async def empty_gen():
            yield f"data: {json.dumps({'type': 'error', 'error': 'No relevant content found'})}\n\n"

        return StreamingResponse(empty_gen(), media_type="text/event-stream")

    context = "\n\n".join(f"[Page {r['page_num']}] {r['text']}" for r in results)

    # Send sources first
    async def stream_gen():
        sources_data = [
            {
                "page_num": r["page_num"],
                "text": r["text"][:200],
                "score": round(r["score"], 3),
            }
            for r in results
        ]
        yield f"data: {json.dumps({'type': 'sources', 'sources': sources_data})}\n\n"

        from .llm import ask_groq_stream

        async for chunk in ask_groq_stream(req.query, context):
            yield chunk

    return StreamingResponse(stream_gen(), media_type="text/event-stream")


import json


@app.delete("/documents/{doc_id}", response_model=DeleteResponse)
async def delete_document(doc_id: str):
    """Delete a document and its embeddings from the vector store."""
    vs = get_store()

    # Check if document exists by searching for it
    results = vs.collection.get(where={"doc_id": doc_id}, limit=1)
    if not results["ids"]:
        raise HTTPException(404, f"Document {doc_id} not found")

    # Delete from vector store
    vs.delete_document(doc_id)

    # Delete uploaded file
    file_path = UPLOAD_DIR / f"{doc_id}.pdf"
    file_path.unlink(missing_ok=True)

    return DeleteResponse(
        doc_id=doc_id,
        deleted=True,
        message=f"Document {doc_id} and its embeddings deleted successfully",
    )


@app.get("/documents")
async def list_documents():
    """List all uploaded documents."""
    vs = get_store()
    results = vs.collection.get()

    # Group by doc_id
    docs = {}
    if results["metadatas"]:
        for meta in results["metadatas"]:
            doc_id = meta.get("doc_id", "")
            if doc_id and doc_id not in docs:
                docs[doc_id] = {"doc_id": doc_id, "chunks": 0}
            if doc_id:
                docs[doc_id]["chunks"] += 1

    # Add filename from upload directory
    for doc_id, info in docs.items():
        file_path = UPLOAD_DIR / f"{doc_id}.pdf"
        if file_path.exists():
            info["filename"] = file_path.name
            info["size"] = file_path.stat().st_size
        else:
            info["filename"] = "unknown"
            info["size"] = 0

    return {"documents": list(docs.values())}


# Serve frontend static files — mounted last so it doesn't shadow API routes
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
