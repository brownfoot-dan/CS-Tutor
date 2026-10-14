"""
rag/rag_chat.py

Axiom RAG chat — retrieves relevant chunks from your notes
before every answer, so Axiom can answer from YOUR documents.

Usage:
    py rag/rag_chat.py
"""

import os
import sys

os.environ.setdefault("PYTHONUTF8", "1")

from pathlib import Path

import ollama
import chromadb
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_NAME = "axiom"
EMBED_MODEL = "nomic-embed-text"
DB_DIR = Path(__file__).parent / "vectorstore"
COLLECTION_NAME = "axiom_notes"
TOP_K = 4           # number of chunks to retrieve per query
MIN_RELEVANCE = 0.3 # cosine distance threshold (lower = more similar)

console = Console()

BANNER = """
+---------------------------------------------+
|         AXIOM  -  CS Tutor  [RAG mode]       |
|   Answering from your notes + training data  |
|   Type  /exit  to quit                       |
|   Type  /clear to reset the conversation     |
|   Type  /sources to see last retrieved docs  |
+---------------------------------------------+
"""

# ── Vector store ──────────────────────────────────────────────────────────────

def load_collection():
    if not DB_DIR.exists():
        console.print("[bold red]No vector store found.[/]")
        console.print("Run  [bold cyan]py rag/ingest.py[/]  first to index your documents.")
        sys.exit(1)
    client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        return client.get_collection(COLLECTION_NAME)
    except Exception:
        console.print("[bold red]Collection not found.[/] Run  [bold cyan]py rag/ingest.py[/]  first.")
        sys.exit(1)


def retrieve(collection, query: str) -> list[dict]:
    """Embed the query and retrieve the top-k most relevant chunks."""
    response = ollama.embed(model=EMBED_MODEL, input=[query])
    query_embedding = response["embeddings"][0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        if dist <= (1 - MIN_RELEVANCE):  # cosine distance: lower = more similar
            chunks.append({"text": doc, "source": meta["source"], "distance": dist})

    return chunks


def build_context_prompt(chunks: list[dict]) -> str:
    """Format retrieved chunks into a context block for the system message."""
    if not chunks:
        return ""
    parts = ["The following notes are relevant to the student's question. Use them to inform your answer:\n"]
    for i, chunk in enumerate(chunks, 1):
        parts.append(f"--- Note {i} (from: {chunk['source']}) ---\n{chunk['text']}\n")
    return "\n".join(parts)


# ── Chat ──────────────────────────────────────────────────────────────────────

def get_response(messages: list[dict]) -> str:
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return response.message.content


def main():
    collection = load_collection()
    count = collection.count()
    console.print(BANNER, style="bold cyan")
    console.print(f"[dim]Vector store loaded — {count} chunks from your documents.[/]\n")

    messages: list[dict] = []
    last_sources: list[dict] = []

    while True:
        try:
            user_input = console.input("[bold green]You -> [/]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/]")
            sys.exit(0)

        if not user_input:
            continue

        # Commands
        if user_input.lower() in ("/exit", "/quit"):
            console.print("[dim]Goodbye! Keep learning![/]")
            break

        if user_input.lower() == "/clear":
            messages.clear()
            console.clear()
            console.print(BANNER, style="bold cyan")
            console.print("[dim]Conversation cleared.[/]\n")
            continue

        if user_input.lower() == "/sources":
            if not last_sources:
                console.print("[dim]No sources retrieved yet.[/]\n")
            else:
                for s in last_sources:
                    console.print(f"  [cyan]{s['source']}[/] (similarity: {1 - s['distance']:.0%})")
                console.print()
            continue

        # Retrieve relevant chunks from the vector store
        with console.status("[dim]Searching your notes...[/]", spinner="dots"):
            chunks = retrieve(collection, user_input)
        last_sources = chunks

        # Build the message list — inject context as a system turn
        context = build_context_prompt(chunks)

        # We inject context fresh each turn (not accumulated in history)
        # so the context window doesn't fill up with repeated note chunks
        rag_messages = []
        if context:
            rag_messages.append({"role": "system", "content": context})
            console.print(f"[dim]  Retrieved {len(chunks)} relevant chunk(s) from your notes[/]")
        else:
            console.print("[dim]  No relevant notes found — answering from training data[/]")

        rag_messages += messages + [{"role": "user", "content": user_input}]

        # Get Axiom's response
        try:
            with console.status("[bold cyan]Axiom is thinking...[/]", spinner="dots"):
                response_text = get_response(rag_messages)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {e}")
            continue

        # Add to conversation history (without the injected context)
        messages.append({"role": "user", "content": user_input})
        messages.append({"role": "assistant", "content": response_text})

        # Render response
        md = Markdown(response_text)
        panel = Panel(
            md,
            title="[bold cyan]Axiom[/]",
            border_style="cyan",
            padding=(1, 2),
        )
        console.print(panel)
        console.print()


if __name__ == "__main__":
    main()
