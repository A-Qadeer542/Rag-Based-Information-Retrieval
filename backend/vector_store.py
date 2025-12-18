from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class VectorStore:
    """A lightweight FAISS-backed vector store for RAG retrieval."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model_name = model_name
        self.embedder = SentenceTransformer(model_name)
        self.dimension = self.embedder.get_sentence_embedding_dimension()
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[str] = []

    @property
    def is_ready(self) -> bool:
        return self.index is not None and len(self.chunks) > 0

    def _encode(self, texts: List[str]) -> np.ndarray:
        embeddings = self.embedder.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
        return embeddings.astype("float32")

    def build(self, chunks: List[str]) -> None:
        if not chunks:
            raise ValueError("Cannot build vector store with no chunks.")

        embeddings = self._encode(chunks)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings)
        self.chunks = chunks
        logger.info("Vector store built with %s chunks.", len(chunks))

    def search(
        self, query: str, top_k: int = 4, score_threshold: float = 0.0
    ) -> List[Tuple[str, float]]:
        if not self.is_ready or self.index is None:
            raise ValueError("Vector store is not initialized. Upload a PDF first.")

        query_embedding = self._encode([query])
        scores, indices = self.index.search(query_embedding, top_k)
        scored_results: List[Tuple[str, float]] = []

        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue
            if score < score_threshold:
                continue
            scored_results.append((self.chunks[idx], float(score)))

        logger.debug("Retrieved %s context chunks for query.", len(scored_results))
        return scored_results

