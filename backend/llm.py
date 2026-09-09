"""Groq LLM integration for answering questions."""

import os
import json
from typing import AsyncGenerator

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

SYSTEM_PROMPT = """You are a helpful document assistant. Answer questions based ONLY on the provided context.
If the context doesn't contain enough information, say so — don't make things up.
Cite the page numbers when referencing specific information from the document."""


def ask_groq(query: str, context: str) -> str:
    """Send a question + context to Groq's Llama 3 and return the answer (non-streaming)."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return (
            "GROQ_API_KEY not set. Create a .env file with your API key. "
            "Get one free at https://console.groq.com"
        )

    client = Groq(api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"Sorry, the LLM call failed: {str(e)}"


async def ask_groq_stream(query: str, context: str) -> AsyncGenerator[str, None]:
    """Stream answer from Groq as SSE events."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        yield f"data: {json.dumps({'type': 'error', 'error': 'GROQ_API_KEY not set'})}\n\n"
        return

    client = Groq(api_key=api_key)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
    ]

    try:
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk.choices[0].delta.content})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
