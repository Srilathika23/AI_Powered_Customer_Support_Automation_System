"""
Task 6: RAG Pipeline
====================
Loads company documents from docs/*.txt, splits them into retrievable
chunks, and scores chunks against a customer query using local keyword
overlap (TF-style scoring) - no embedding model, no API key, and no
internet connection required.

This trades some of the nuance of true semantic embeddings for a
pipeline that installs in seconds and runs anywhere Python runs.
"""

import os
import re
from collections import Counter

# Path to knowledge base documents
DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs")

DOCUMENTS = {
    "company_policy":   "company_policy.txt",
    "pricing_guide":     "pricing_guide.txt",
    "technical_manual":  "technical_manual.txt",
    "faq":               "faq.txt",
}

QA_STYLE_SOURCES = {"faq"}

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "to", "of",
    "and", "or", "in", "on", "for", "with", "my", "i", "do", "does", "what",
    "how", "can", "you", "your", "it", "this", "that", "have", "has", "had",
    "will", "would", "could", "should", "did", "am", "as", "at", "by", "from",
}


class Chunk:
    __slots__ = ("text", "source", "tokens")

    def __init__(self, text: str, source: str):
        self.text = text.strip()
        self.source = source
        self.tokens = Counter(_tokenize(self.text))


def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _is_heading_only(block: str) -> bool:
    lines = [ln for ln in block.splitlines() if ln.strip()]
    if not lines or len(lines) > 2:
        return False
    if len(lines) == 2 and re.fullmatch(r"[-=]{3,}", lines[1].strip()):
        return True
    if len(lines) == 1 and len(lines[0]) < 40:
        return True
    return False


def _merge_headings(blocks: list[str]) -> list[str]:
    merged: list[str] = []
    pending_heading = ""
    for block in blocks:
        if _is_heading_only(block):
            pending_heading = (pending_heading + "\n" + block).strip() if pending_heading else block
            continue
        if pending_heading:
            merged.append(pending_heading + "\n" + block)
            pending_heading = ""
        else:
            merged.append(block)
    if pending_heading:
        merged.append(pending_heading)
    return merged


def _load_qa_chunks(filepath: str, source: str) -> list[Chunk]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    blocks = _merge_headings(blocks)
    return [Chunk(block, source) for block in blocks]


def _load_paragraph_chunks(filepath: str, source: str) -> list[Chunk]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]
    blocks = _merge_headings(blocks)
    return [Chunk(block, source) for block in blocks]


def load_chunks() -> list[Chunk]:
    chunks: list[Chunk] = []
    for source, filename in DOCUMENTS.items():
        filepath = os.path.join(DOCS_DIR, filename)

        if source in QA_STYLE_SOURCES:
            new_chunks = _load_qa_chunks(filepath, source)
        else:
            new_chunks = _load_paragraph_chunks(filepath, source)

        chunks.extend(new_chunks)
        print(f"[RAG] Loaded '{source}' as {len(new_chunks)} chunk(s).")

    print(f"[RAG] Loaded {len(DOCUMENTS)} knowledge-base documents -> {len(chunks)} total chunks.")
    return chunks


def _score(query_tokens: Counter, chunk: Chunk) -> int:
    return sum(count for tok, count in query_tokens.items() if tok in chunk.tokens)


def retrieve_context(chunks: list[Chunk], query: str, k: int = 3) -> str:
    query_tokens = Counter(_tokenize(query))
    if not query_tokens:
        return "No relevant information found in the knowledge base."

    scored = [(chunk, _score(query_tokens, chunk)) for chunk in chunks]
    scored = [(c, s) for c, s in scored if s > 0]
    scored.sort(key=lambda pair: pair[1], reverse=True)

    top = scored[:k] if scored else []
    if not top:
        return "No relevant information found in the knowledge base."

    context_parts = [f"[Source: {chunk.source}]\n{chunk.text}" for chunk, _ in top]
    print(f"[RAG] Retrieved {len(top)} chunk(s) for query: {query!r}")
    for chunk, score in top:
        print(f"       [kept] score={score} source={chunk.source}")

    return "\n\n---\n\n".join(context_parts)


_chunks: list[Chunk] | None = None


def get_chunks() -> list[Chunk]:
    global _chunks
    if _chunks is None:
        _chunks = load_chunks()
    return _chunks