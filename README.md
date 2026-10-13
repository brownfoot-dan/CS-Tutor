# Axiom — Your CS Tutor 🎓

A custom AI tutor for university-level computer science, built with [Ollama](https://ollama.com) and Python.

---

## Project structure

```
cs-tutor/
├── Modelfile          ← Defines Axiom (system prompt, behaviour, base model)
├── chat.py            ← Terminal chat app
├── requirements.txt   ← Python dependencies
└── README.md
```

**Coming soon:**
```
cs-tutor/
├── rag/
│   ├── ingest.py      ← Load your notes/PDFs into a vector store
│   └── rag_chat.py    ← Chat app that retrieves from your documents
```

---

## Setup

### 1. Sign in to Ollama (for cloud model access)

```powershell
ollama signin
```

> This gives you access to `gemma4:cloud`, which is included in the **free plan** and powers Axiom.

### 2. Build your custom model

```powershell
ollama create axiom -f Modelfile
```

You should see `transferring model data` then `success`. Axiom is now a model on your machine.

### 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 4. Chat with Axiom

```powershell
python chat.py
```

---

## Usage

```
You → What is a binary search tree?
You → Can you explain recursion with an example?
You → /clear    ← reset the conversation
You → /exit     ← quit
```

---

## Customising Axiom

Edit `Modelfile` to change:
- **`SYSTEM`** — Axiom's personality, rules, and expertise
- **`PARAMETER temperature`** — higher = more creative, lower = more accurate
- **`PARAMETER num_ctx`** — how much conversation history it remembers

After editing, rebuild:
```powershell
ollama create axiom -f Modelfile
```

---

## Upgrading to RAG (Phase 2)

Once RAG is added, Axiom will be able to answer questions from **your own lecture notes, textbooks, and course materials** — not just its training data. See the `rag/` folder when it's ready.
