"""Embedding generation and vector storage with ChromaDB."""

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "pdf_chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


class VectorStore:
    """Manages embeddings and similarity search for document chunks."""

    def __init__(self, persist_dir: str | Path = CHROMA_DIR):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)

        self.client = chromadb.PersistentClient(str(self.persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        # Using SentenceTransformer locally — no API key needed
        self.model = SentenceTransformer(MODEL_NAME)

    def add_document(self, doc_id: str, chunks: list[dict]) -> int:
        """Embed and store document chunks in ChromaDB.

        Args:
            doc_id: Unique document identifier.
            chunks: List of chunks from processor.chunk_text().

        Returns:
            Number of chunks added.
        """
        texts = [c["text"] for c in chunks]
        metadatas = [
            {"doc_id": doc_id, "page_num": c["page_num"], "chunk_index": i}
            for i, c in enumerate(chunks)
        ]
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

        embeddings = self.model.encode(texts, show_progress_bar=False).tolist()

        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids,
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Find the most relevant chunks for a query.

        Args:
            query: User's question.
            top_k: Number of chunks to return.

        Returns:
            List of dicts with text, page_num, and score.
        """
        query_embedding = self.model.encode(query).tolist()

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        chunks = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                chunks.append({
                    "text": doc,
                    "page_num": results["metadatas"][0][i].get("page_num", 0),
                    "score": results["distances"][0][i] if results.get("distances") else 0,
                    "doc_id": results["metadatas"][0][i].get("doc_id", ""),
                })
        return chunks

    def delete_document(self, doc_id: str) -> None:
        """Remove all chunks for a document."""
        self.collection.delete(where={"doc_id": doc_id})
