"""Document chunking service — splits text into overlapping chunks for embedding."""

from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    token_count: int


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text."""
    return len(text) // 4


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
) -> list[TextChunk]:
    """Split text into overlapping chunks by token estimate.

    Args:
        text: The full text to chunk.
        chunk_size: Target tokens per chunk.
        chunk_overlap: Overlap tokens between consecutive chunks.

    Returns:
        List of TextChunk objects.
    """
    if not text.strip():
        return []

    # Split on paragraph boundaries first, then sentence
    paragraphs = text.split("\n\n")
    sentences: list[str] = []
    for para in paragraphs:
        # Keep paragraph boundaries as markers
        if para.strip():
            sentences.extend(_split_sentences(para))
            sentences.append("\n\n")

    # Remove trailing separator
    if sentences and sentences[-1] == "\n\n":
        sentences.pop()

    chunks: list[TextChunk] = []
    current_sentences: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sent_tokens = estimate_tokens(sentence)

        if current_tokens + sent_tokens > chunk_size and current_sentences:
            # Emit current chunk
            chunk_text_content = " ".join(
                s for s in current_sentences if s != "\n\n"
            ).replace("  ", " ").strip()

            if chunk_text_content:
                chunks.append(TextChunk(
                    content=chunk_text_content,
                    chunk_index=len(chunks),
                    token_count=estimate_tokens(chunk_text_content),
                ))

            # Keep overlap
            overlap_tokens = 0
            overlap_start = len(current_sentences)
            for i in range(len(current_sentences) - 1, -1, -1):
                overlap_tokens += estimate_tokens(current_sentences[i])
                if overlap_tokens >= chunk_overlap:
                    overlap_start = i
                    break
            current_sentences = current_sentences[overlap_start:]
            current_tokens = sum(estimate_tokens(s) for s in current_sentences)

        current_sentences.append(sentence)
        current_tokens += sent_tokens

    # Final chunk
    if current_sentences:
        chunk_text_content = " ".join(
            s for s in current_sentences if s != "\n\n"
        ).replace("  ", " ").strip()
        if chunk_text_content:
            chunks.append(TextChunk(
                content=chunk_text_content,
                chunk_index=len(chunks),
                token_count=estimate_tokens(chunk_text_content),
            ))

    return chunks


def _split_sentences(text: str) -> list[str]:
    """Simple sentence splitter on period/question/exclamation followed by space."""
    import re
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p for p in parts if p.strip()]
