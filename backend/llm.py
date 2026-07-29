"""Groq LLM integration for answering questions."""

import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

SYSTEM_PROMPT = """You are a helpful document assistant. Answer questions based ONLY on the provided context.
If the context doesn't contain enough information, say so — don't make things up.
Cite the page numbers when referencing specific information from the document."""


def ask_groq(query: str, context: str) -> str:
    """Send a question + context to Groq's Llama 3 and return the answer.

    Args:
        query: The user's question.
        context: Relevant document chunks with page numbers.

    Returns:
        The LLM's answer as a string.
    """
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
