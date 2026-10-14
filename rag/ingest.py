"""
rag/ingest.py

Loads documents from rag/docs/, chunks them, embeds them with
nomic-embed-text via Ollama, and stores them in a local ChromaDB
vector store.

Supported file types: .txt, .md, .pdf

Usage:
    py rag/ingest.py
"""

import os
import sys
import hashlib
from pathlib import Path

import ollama
import chromadb

# ── Config ────────────────────────────────────────────────────────────────────
DOCS_DIR = Path(__file__).parent / "docs"
DB_DIR = Path(__file__).parent / "vectorstore"
COLLECTION_NAME = "axiom_notes"
EMBED_MODEL = "nomic-embed-text"
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 50      # overlap between chunks


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_pdf_file(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("  [!] pypdf not installed — skipping PDF. Run: py -m pip install pypdf")
        return ""
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".txt", ".md"):
        return load_text_file(path)
    elif suffix == ".pdf":
        return load_pdf_file(path)
    return ""


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping character-level chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 20]  # drop tiny remnants


def doc_id(source: str, index: int) -> str:
    """Stable unique ID for a chunk."""
    raw = f"{source}::{index}"
    return hashlib.md5(raw.encode()).hexdigest()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of strings using Ollama."""
    response = ollama.embed(model=EMBED_MODEL, input=texts)
    return response["embeddings"]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not DOCS_DIR.exists() or not any(DOCS_DIR.iterdir()):
        print(f"[!] No documents found in {DOCS_DIR}")
        print("    Drop .txt, .md, or .pdf files there and run this again.")
        sys.exit(0)

    # Connect to (or create) the local ChromaDB
    DB_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    docs = list(DOCS_DIR.rglob("*"))
    supported = [d for d in docs if d.suffix.lower() in (".txt", ".md", ".pdf") and d.is_file()]

    if not supported:
        print(f"[!] No .txt, .md, or .pdf files found in {DOCS_DIR}")
        sys.exit(0)

    print(f"Found {len(supported)} document(s). Embedding with '{EMBED_MODEL}'...\n")

    total_chunks = 0
    for doc_path in supported:
        print(f"  Loading: {doc_path.name}")
        text = load_document(doc_path)
        if not text.strip():
            print(f"    [!] Empty or unreadable — skipping.")
            continue

        chunks = chunk_text(text)
        print(f"    -> {len(chunks)} chunks")

        # Embed in batches of 32
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            embeddings = embed_texts(batch)
            ids = [doc_id(doc_path.name, i + j) for j in range(len(batch))]
            metadatas = [{"source": doc_path.name, "chunk": i + j} for j in range(len(batch))]

            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=batch,
                metadatas=metadatas,
            )
        total_chunks += len(chunks)

    print(f"\nDone! {total_chunks} chunks stored in {DB_DIR}")
    print("Run  py rag/rag_chat.py  to chat with your notes.")


if __name__ == "__main__":
    main()
