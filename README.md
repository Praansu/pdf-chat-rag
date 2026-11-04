# PDF Chat (RAG)

Upload a PDF, ask questions about it. Built this because I kept re-reading long PDFs for class.

PyMuPDF pulls the text, sentence-transformers + ChromaDB find the relevant bits, Groq Llama 3 writes the answer. Streaming + you can delete docs without restarting.

## how to run
```
pip install -r requirements.txt
python app.py  # streamlit, opens in browser
```

Add your GROQ key in `.env`. PDFs go in `uploads/`.

## stack
Python, Streamlit, ChromaDB, PyMuPDF, Groq

Note: scanned PDFs don't work great. Need OCR, haven't added it yet.
