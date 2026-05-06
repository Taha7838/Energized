# Energized — Local Dev Setup (Windows 11)

## What runs where

| Service        | URL                        | What it does                              |
|----------------|----------------------------|-------------------------------------------|
| Frontend       | http://localhost:5173      | React UI (Researcher + RAG pages)         |
| Agent Backend  | http://localhost:8000      | CrewAI multi-agent researcher             |
| RAG Backend    | http://localhost:8001      | PDF upload + Q&A pipeline                 |
| Streamlit      | http://localhost:8501      | Standalone RAG UI (optional)              |

The frontend proxies `/api/*` → 8000 and `/rag/api/*` → 8001 — you never
call backends directly in the browser.

---

## Prerequisites

Install these once:

- **Python 3.11** — https://www.python.org/downloads/ (check "Add to PATH")
- **Node.js 20+** — https://nodejs.org/en/download

Verify in a new terminal:
```
python --version   # 3.11.x
node --version     # v20.x or higher
npm --version
```

---

## API Keys

You need two:

- **Gemini** — https://aistudio.google.com/app/apikey (free tier works)
- **Tavily** — https://app.tavily.com (free tier: 1000 searches/month)

---

## One-time setup

Open **three separate** PowerShell/Command Prompt windows. Run each block in
the corresponding window — they all need to stay running.

### Window 1 — Agent Backend

```powershell
cd path\to\Energized-main\agent\backend

# Create venv
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your .env from the example
copy .env.example .env
# Open .env in notepad and fill in your keys:
notepad .env
```

### Window 2 — RAG Backend

```powershell
cd path\to\Energized-main\rag

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env
notepad .env    # only needs GEMINI_API_KEY
```

### Window 3 — Frontend

```powershell
cd path\to\Energized-main\agent\frontend

npm install
```

---

## Starting everything (daily use)

### Window 1 — Agent Backend

```powershell
cd path\to\Energized-main\agent\backend
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

Expected output:
```
Energy Researcher Agent — Backend Starting
  LLM Model     : gemini-2.5-flash-lite
  ...
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Window 2 — RAG Backend

```powershell
cd path\to\Energized-main\rag
.venv\Scripts\activate
uvicorn main:app --reload --port 8001
```

Expected output:
```
INFO:     RAG backend starting up.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

### Window 3 — Frontend

```powershell
cd path\to\Energized-main\agent\frontend
npm run dev
```

Expected output:
```
  VITE v8.x.x  ready in Xms
  ➜  Local:   http://localhost:5173/
```

Open http://localhost:5173 in your browser.

---

## Optional: Streamlit RAG UI

The `rag/app.py` is a standalone Streamlit interface for the RAG pipeline —
separate from the React frontend, talks directly to Gemini without the
FastAPI layer.

```powershell
cd path\to\Energized-main\rag
.venv\Scripts\activate

# Set key for this session (Streamlit reads env vars directly)
$env:GEMINI_API_KEY = "your_key_here"

streamlit run app.py
```

---

## Health checks

Verify backends are up before using the UI:

```
http://localhost:8000/health   → {"status":"ok","model":"gemini-2.5-flash-lite"}
http://localhost:8001/health   → {"status":"ok","indexed_chunks":0}
```

---

## Troubleshooting

**`ModuleNotFoundError`** — make sure you activated the venv in the right
window (`.venv\Scripts\activate`).

**Agent backend exits at startup** — your `.env` is missing or has placeholder
keys. The startup validator calls `sys.exit(1)` intentionally.

**RAG backend 500 on `/query`** — no documents indexed yet. Upload a PDF
first via the RAG page.

**Frontend shows "Connection to server lost"** — one of the backends isn't
running. Check both terminal windows for errors.

**ChromaDB errors on re-start** — usually safe to ignore on first run; it
creates `memory/chroma_store/` and `rag/chroma_db/` automatically.

**`sentence-transformers` download on first run** — the embedding model
(`all-MiniLM-L6-v2`, ~90MB) downloads once to your HuggingFace cache.
Normal.

---

## Project layout

```
Energized-main/
├── agent/
│   ├── backend/          ← FastAPI + CrewAI (port 8000)
│   │   ├── core/         ← settings (reads .env)
│   │   ├── crew/         ← agents + tasks + runner
│   │   ├── memory/       ← ChromaDB vector store
│   │   ├── output/       ← knowledge_base.txt (appended each run)
│   │   ├── schemas/      ← Pydantic models
│   │   ├── tools/        ← Tavily search tool wrapper
│   │   ├── .env          ← YOUR KEYS (gitignored)
│   │   └── requirements.txt
│   └── frontend/         ← React + Vite (port 5173)
│       └── src/
│           ├── pages/    ← ResearcherPage, RagPage
│           └── api/      ← client.js (axios + SSE)
└── rag/
    ├── main.py           ← FastAPI RAG backend (port 8001)
    ├── rag_chain.py      ← PDF ingestion + retrieval + Gemini
    ├── app.py            ← Streamlit standalone UI (optional, port 8501)
    ├── .env              ← YOUR KEY (gitignored)
    └── requirements.txt
```
