"""Pydantic models for request/response schemas."""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    size: int
    chunks: int
    pages: int


class ChatRequest(BaseModel):
    query: str
    doc_id: str | None = None
    top_k: int = 3


class Source(BaseModel):
    page_num: int
    text: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


class DeleteResponse(BaseModel):
    doc_id: str
    deleted: bool
    message: str
