from __future__ import annotations

import logging
from pathlib import Path
from typing import List

from langchain_community.document_loaders import PyPDFLoader

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100


def chunk_text(
    text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """Split text into overlapping character chunks."""
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap.")

    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []

    chunks: List[str] = []
    start = 0
    text_length = len(cleaned_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(cleaned_text[start:end])
        if end == text_length:
            break
        start = end - chunk_overlap

    logger.debug("Chunked text into %s segments.", len(chunks))
    return chunks


def load_and_chunk_pdf(
    file_path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Extract text from the PDF and return overlapping chunks.

    Returns:
        List[str]: The extracted text chunks ready for embedding.
    """
    if not isinstance(file_path, Path):
        raise TypeError("file_path must be a pathlib.Path instance.")
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    loader = PyPDFLoader(str(file_path))
    documents = loader.load()
    if not documents:
        logger.warning("No content extracted from PDF: %s", file_path)
        return []

    full_text = "\n".join(doc.page_content for doc in documents if doc.page_content)
    if not full_text.strip():
        logger.warning("Extracted PDF text is empty after stripping whitespace: %s", file_path)
        return []

    chunks = chunk_text(full_text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    logger.info("Extracted %s text chunks from PDF.", len(chunks))
    return chunks


