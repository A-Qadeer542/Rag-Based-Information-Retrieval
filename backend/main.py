from __future__ import annotations

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Dict

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool

from backend.rag_pipeline import RAGPipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("backend")

app = FastAPI(title="RAG-Based Information Retrieval", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = RAGPipeline()


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        contents = await file.read()
        tmp_file.write(contents)
        temp_path = Path(tmp_file.name)

    try:
        chunk_count = await run_in_threadpool(pipeline.ingest_pdf, temp_path)
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to process uploaded PDF.")
        raise HTTPException(
            status_code=500,
            detail="Failed to process PDF. Please ensure the file is a readable PDF.",
        ) from exc
    finally:
        temp_path.unlink(missing_ok=True)

    return JSONResponse(
        status_code=200,
        content={"message": "PDF processed successfully.", "chunks": chunk_count},
    )


@app.post("/ask")
async def ask_question(payload: QuestionRequest) -> JSONResponse:
    if not pipeline.is_ready:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF before asking questions.",
        )

    try:
        answer: str = await run_in_threadpool(
            pipeline.answer_question, payload.question
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Failed to generate answer.")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer from the uploaded document.",
        ) from exc

    return JSONResponse(status_code=200, content={"answer": answer})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


