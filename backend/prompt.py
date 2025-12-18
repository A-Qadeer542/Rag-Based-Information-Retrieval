from __future__ import annotations

from typing import List

REFUSAL_MESSAGE = "I cannot find this information in the provided document."

SYSTEM_PROMPT = (
    "You are an information retrieval assistant.\n"
    "Answer only using the provided context.\n"
    f'If the answer is not in the context, respond exactly with: "{REFUSAL_MESSAGE}".\n'
    "Do not use any external knowledge or make up information."
)


def build_prompt(context_chunks: List[str], question: str) -> str:
    """Constructs a strict RAG prompt using the provided context and question."""
    context_block = "\n\n".join(
        f"- {chunk.strip()}" for chunk in context_chunks if chunk.strip()
    )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        "Context:\n"
        f"{context_block}\n\n"
        "Question:\n"
        f"{question.strip()}\n\n"
        "Answer:"
    )

