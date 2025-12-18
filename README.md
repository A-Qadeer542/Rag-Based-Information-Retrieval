# Rag-Based Information Retrieval

A fully local RAG demo that lets you upload a PDF and ask questions. Answers are **only** drawn from your uploaded document. If the information is missing, the app replies with the exact refusal message:

`I cannot find this information in the provided document.`

No external APIs or paid services are used—everything runs locally.

## Tech Stack
- Backend: FastAPI, FAISS, sentence-transformers (`all-MiniLM-L6-v2`), PyPDFLoader, Ollama (`llama3`)
- Frontend: Static HTML, JavaScript, CSS

## Prerequisites
- Python 3.10+
- PowerShell or any shell capable of running `uvicorn`
- [Ollama](https://ollama.ai) installed locally

## Setup
1) Install Ollama and pull the model
```bash
ollama pull llama3
```

2) Create a virtual environment and install backend deps
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate  # or source .venv/bin/activate on macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt
```

3) Run the backend API
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Health check: http://localhost:8000/health

4) Open the frontend
- Option A: open `frontend/index.html` directly in your browser.
- Option B (recommended for CORS consistency):
```bash
python -m http.server 5500 --directory frontend
# then visit http://localhost:5500
```

## Usage
1. Upload a PDF via the UI (chunks of 800 chars, 100 overlap are embedded into FAISS).
2. Once indexed, the question box unlocks. Ask a question.
3. The app retrieves the top 4 relevant chunks and queries `llama3` through Ollama with a strict prompt.
4. If the answer is not explicitly in the retrieved context, the response is:
   `I cannot find this information in the provided document.`

## Notes
- The backend stores embeddings in-memory; uploading a new PDF replaces the previous index.
- Ensure Ollama is running locally before asking questions.
- All logging uses the standard `logging` module; no external telemetry is used.
