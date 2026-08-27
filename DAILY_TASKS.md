# Daily Tasks — pdf-chat-rag

Pick **one** task per day (5–10 min). Commit via PR so every change is reviewable and explainable in interviews.

## Backend (FastAPI + Python)

- [ ] Add type hints to one function in `backend/embeddings.py` or `backend/processor.py`
- [ ] Write one unit test for PDF chunking logic in `backend/test_processor.py` (create if missing)
- [ ] Refactor one function in `backend/main.py` to reduce complexity
- [ ] Add docstring + example to one FastAPI endpoint in `backend/main.py`
- [ ] Add one integration test for `/upload` + `/chat` flow in `backend/test_integration.py`
- [ ] Replace one `print()` with proper `logging` call
- [ ] Add input validation (Pydantic) to one endpoint parameter
- [ ] Extract magic number (chunk size, overlap) to a constant at top of file

## Frontend (Vanilla HTML/JS)

- [ ] Add one accessibility improvement (aria-label, focus style, semantic HTML) in `frontend/index.html`
- [ ] Extract one inline style to CSS class
- [ ] Improve error message UX for one failure case
- [ ] Improve mobile layout for one section (media query)

## Docs / Meta

- [ ] Update `README.md` with one new usage example or clarification
- [ ] Add one entry to `CHANGELOG.md` (create if missing) for recent change
- [ ] Fix one typo or unclear sentence in `README.md`
- [ ] Add one badge to `README.md` (e.g., Python version, license)

## Quality

- [ ] Run `ruff check backend/` → fix one lint warning
- [ ] Run `black --check backend/` → format one file
- [ ] Add `pre-commit` hook config (`.pre-commit-config.yaml`) if missing

---

**How to use:** Each morning, pick ONE unchecked item. Do it. Commit with message like `refactor: extract chunking constants in processor.py`. Open PR. Merge after review. Check the box.