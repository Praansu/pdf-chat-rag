"""PDF parsing and text chunking."""

from pathlib import Path

import fitz  # PyMuPDF


def extract_text(pdf_path: str | Path) -> list[dict]:
    """Extract text from a PDF file, returning pages with metadata.

    Returns a list of dicts: {page_num, text, char_count}
    """
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text().strip()
        if text:
            pages.append({
                "page_num": i + 1,
                "text": text,
                "char_count": len(text),
            })
    doc.close()
    return pages


def chunk_text(pages: list[dict], max_chars: int = 1000, overlap: int = 100) -> list[dict]:
    """Split page text into overlapping sentence-based chunks.

    Sentence-based chunking preserves meaning better than fixed-size splits.
    Each chunk includes source page number for citation.
    """
    chunks = []
    for page in pages:
        text = page["text"]
        sentences = _split_sentences(text)

        current_chunk = ""
        for sentence in sentences:
            # If adding this sentence would exceed max_chars, save current chunk
            if len(current_chunk) + len(sentence) > max_chars and current_chunk:
                chunks.append(_make_chunk(current_chunk, page["page_num"]))
                # Keep overlap chars from end of previous chunk
                current_chunk = current_chunk[-overlap:] if overlap > 0 else ""

            current_chunk += sentence + " "

        # Don't forget the last chunk
        if current_chunk.strip():
            chunks.append(_make_chunk(current_chunk.strip(), page["page_num"]))

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences on sentence boundaries."""
    import re
    # Split on sentence endings while keeping the delimiter
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def _make_chunk(text: str, page_num: int) -> dict:
    return {
        "text": text,
        "page_num": page_num,
        "char_count": len(text),
    }
