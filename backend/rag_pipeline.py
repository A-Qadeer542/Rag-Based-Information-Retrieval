from __future__ import annotations

import logging
from pathlib import Path
from typing import List

import httpx

from backend.pdf_loader import load_and_chunk_pdf
from backend.prompt import REFUSAL_MESSAGE, build_prompt
from backend.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Pipeline for PDF ingestion and retrieval-augmented generation."""

    def __init__(
        self,
        model_name: str = "llama3",
        ollama_url: str = "http://localhost:11434",
        top_k: int = 4,
    ) -> None:
        self.model_name = model_name
        self.ollama_url = ollama_url.rstrip("/")
        self.top_k = top_k
        self.vector_store = VectorStore()
        self._client = httpx.Client(timeout=60)

    @property
    def is_ready(self) -> bool:
        return self.vector_store.is_ready

    def ingest_pdf(self, file_path: Path) -> int:
        """Load a PDF, chunk it, and rebuild the vector store."""
        chunks = load_and_chunk_pdf(file_path)
        if not chunks:
            raise ValueError("No text could be extracted from the PDF.")

        self.vector_store.build(chunks)
        return len(chunks)

    def answer_question(self, question: str) -> str:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")
        if not self.vector_store.is_ready:
            raise RuntimeError("Please upload a PDF before asking questions.")

        retrieval_results = self.vector_store.search(
            question, top_k=self.top_k, score_threshold=0.2
        )
        if not retrieval_results:
            logger.info("No relevant context found; returning refusal message.")
            return REFUSAL_MESSAGE

        contexts: List[str] = [chunk for chunk, _ in retrieval_results]
        prompt = build_prompt(contexts, question)
        logger.debug("Constructed prompt for Ollama with %s context chunks.", len(contexts))

        answer = self._query_ollama(prompt)
        if not answer:
            return REFUSAL_MESSAGE

        return answer.strip()

    def _query_ollama(self, prompt: str) -> str:
        payload = {"model": self.model_name, "prompt": prompt, "stream": False}
        url = f"{self.ollama_url}/api/generate"

        try:
            response = self._client.post(url, json=payload)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.exception("Failed to contact Ollama at %s", url)
            raise RuntimeError("Failed to contact Ollama. Ensure it is running locally.") from exc

        data = response.json()
        answer = data.get("response", "")
        return answer.strip() if isinstance(answer, str) else ""

