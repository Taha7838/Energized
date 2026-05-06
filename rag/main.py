# rag/main.py

import logging
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_chain import RAGChain, TOP_K

load_dotenv(Path(__file__).parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Gemini API key — must be set in .env / environment
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set — /query will fail.")
    logger.info("RAG backend starting up.")
    yield
    logger.info("RAG backend shutting down.")


app = FastAPI(
    title="EnergyRAG Backend",
    description="RAG pipeline for energy documents.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Single shared RAGChain instance for the process lifetime
rag = RAGChain()


# ─────────────────────────────────────────────────────────────────
#  SCHEMAS
# ─────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    question: str
    top_k:    int = TOP_K


class QueryResponse(BaseModel):
    answer:           str
    sources:          list
    retrieved_chunks: list


# ─────────────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "indexed_chunks": rag.store.count()}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Ingest a PDF into the vector store."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    try:
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = rag.ingest(tmp_path)
        return result

    except Exception as e:
        logger.error(f"Ingest failed for {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass


@app.get("/documents")
async def list_documents():
    """Return list of all indexed document names."""
    return {"documents": rag.store.list_documents()}


@app.delete("/documents/{doc_name}")
async def delete_document(doc_name: str):
    """Remove a document and all its chunks from the vector store."""
    docs = rag.store.list_documents()
    if doc_name not in docs:
        raise HTTPException(status_code=404, detail=f"Document '{doc_name}' not found.")
    try:
        rag.store.delete_document(doc_name)
        return {"deleted": doc_name}
    except Exception as e:
        logger.error(f"Delete failed for {doc_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Answer a question using the RAG pipeline."""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured on the server.")

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if rag.store.count() == 0:
        raise HTTPException(status_code=400, detail="No documents indexed yet. Upload a PDF first.")

    try:
        result = rag.query(question, top_k=request.top_k, api_key=GEMINI_API_KEY)
        return result
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))