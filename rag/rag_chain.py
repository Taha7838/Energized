# rag/rag_chain.py

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# ─────────────────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────────────────
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL       = "gemini-2.5-flash"
CHROMA_PATH     = "./chroma_db"
CHUNK_SIZE      = 500
CHUNK_OVERLAP   = 50
TOP_K           = 5

SYSTEM_PROMPT = """You are an expert assistant for energy industry professionals.
You help analysts, engineers, and managers understand technical energy documents.

STRICT RULES YOU MUST FOLLOW:
1. Answer ONLY using the document excerpts provided below.
2. If the answer is NOT present in the excerpts, respond with:
   "I could not find this information in the uploaded documents."
3. Always cite your sources at the end in this format:
   📎 Sources: [Document Name, Page X] | [Document Name, Page Y]
4. Be precise, concise, and professional.
5. Never invent, extrapolate, or guess facts not in the context."""


# ─────────────────────────────────────────────────────────────────
#  DATA CLASSES
# ─────────────────────────────────────────────────────────────────
@dataclass
class Page:
    page_no:  int
    text:     str
    doc_name: str


@dataclass
class Chunk:
    chunk_id:    str
    doc_name:    str
    page_no:     int
    text:        str
    token_count: int


@dataclass
class SearchResult:
    chunk_id: str
    doc_name: str
    page_no:  int
    text:     str
    score:    float


# ─────────────────────────────────────────────────────────────────
#  PIPELINE CLASSES  (identical logic to original app.py)
# ─────────────────────────────────────────────────────────────────
class PDFProcessor:
    """Extracts and cleans text from PDF documents page by page."""

    def extract(self, pdf_path: str) -> List[Page]:
        import fitz
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        doc_name = path.stem
        pages: List[Page] = []
        with fitz.open(pdf_path) as doc:
            for i, page in enumerate(doc):
                raw_text = page.get_text("text")
                cleaned  = self._clean(raw_text)
                if cleaned:
                    pages.append(Page(page_no=i + 1, text=cleaned, doc_name=doc_name))
        return pages

    def _clean(self, text: str) -> str:
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{3,}", " ", text)
        text = re.sub(r"(?i)page\s+\d+", "", text)
        return text.strip()


class TextChunker:
    """Sliding-window token-based chunker."""

    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        import tiktoken
        self.chunk_size = chunk_size
        self.overlap    = overlap
        self._enc       = tiktoken.get_encoding("cl100k_base")

    def chunk(self, pages: List[Page]) -> List[Chunk]:
        all_chunks: List[Chunk] = []
        step = self.chunk_size - self.overlap
        for page in pages:
            tokens = self._enc.encode(page.text)
            if len(tokens) <= self.chunk_size:
                all_chunks.append(Chunk(
                    chunk_id=str(uuid.uuid4()), doc_name=page.doc_name,
                    page_no=page.page_no, text=page.text, token_count=len(tokens)))
                continue
            for start in range(0, len(tokens) - self.overlap, step):
                end        = min(start + self.chunk_size, len(tokens))
                chunk_text = self._enc.decode(tokens[start:end]).strip()
                if chunk_text:
                    all_chunks.append(Chunk(
                        chunk_id=str(uuid.uuid4()), doc_name=page.doc_name,
                        page_no=page.page_no, text=chunk_text, token_count=end - start))
                if end == len(tokens):
                    break
        return all_chunks


# class GeminiEmbedder:
#     """Local sentence-transformers embedder."""

#     def __init__(self, model: str = EMBEDDING_MODEL):
#         from sentence_transformers import SentenceTransformer
#         self.model_name = model
#         self._model     = SentenceTransformer(model)

#     def embed_texts(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
#         return self._model.encode(
#             texts,
#             show_progress_bar    = show_progress,
#             convert_to_numpy     = True,
#             normalize_embeddings = True,
#         ).tolist()

#     def embed_query(self, query: str) -> List[float]:
#         return self._model.encode(
#             query,
#             convert_to_numpy     = True,
#             normalize_embeddings = True,
#         ).tolist()

# rag/rag_chain.py

class GeminiEmbedder:
    """Gemini API embedder — replaces local sentence-transformers."""

    def __init__(self, model: str = "models/gemini-embedding-001"):
        import os
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=os.environ["GEMINI_API_KEY"],
            task_type="RETRIEVAL_DOCUMENT",
        )

    def embed_texts(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        return self._embeddings.embed_documents(texts)

    def embed_query(self, query: str) -> List[float]:
        return self._embeddings.embed_query(query)


class VectorStore:
    """ChromaDB-backed persistent vector store."""

    COLLECTION = "energy_docs"

    def __init__(self, persist_path: str = CHROMA_PATH):
        import chromadb
        from chromadb.config import Settings as ChromaSettings
        self._client = chromadb.PersistentClient(
            path=persist_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._col = self._client.get_or_create_collection(
            name=self.COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        self._col.add(
            ids        = [c.chunk_id for c in chunks],
            embeddings = embeddings,
            documents  = [c.text for c in chunks],
            metadatas  = [{
                "doc_name":    c.doc_name,
                "page_no":     c.page_no,
                "token_count": c.token_count,
            } for c in chunks],
        )

    def search(self, query_embedding: List[float], top_k: int = TOP_K) -> List[SearchResult]:
        if self._col.count() == 0:
            return []
        results = self._col.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._col.count()),
            include=["documents", "metadatas", "distances"],
        )
        out = []
        for i, cid in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i]
            out.append(SearchResult(
                chunk_id=cid,
                doc_name=meta["doc_name"],
                page_no=meta["page_no"],
                text=results["documents"][0][i],
                score=round(1 - results["distances"][0][i], 4),
            ))
        return out

    def list_documents(self) -> List[str]:
        if self._col.count() == 0:
            return []
        return sorted(set(
            m["doc_name"] for m in self._col.get(include=["metadatas"])["metadatas"]
        ))

    def delete_document(self, doc_name: str) -> None:
        self._col.delete(where={"doc_name": doc_name})

    def count(self) -> int:
        return self._col.count()


# ─────────────────────────────────────────────────────────────────
#  RAG CHAIN  (orchestrator — identical logic to original app.py)
# ─────────────────────────────────────────────────────────────────
class RAGChain:
    """PDF → Chunks → Embeddings → VectorDB → Retrieval → Gemini → Answer"""

    def __init__(self):
        self.processor = PDFProcessor()
        self.chunker   = TextChunker()
        self.embedder  = GeminiEmbedder()
        self.store     = VectorStore()

    def ingest(self, pdf_path: str) -> Dict:
        doc_name = Path(pdf_path).stem
        if doc_name in self.store.list_documents():
            existing = self.store._col.get(where={"doc_name": doc_name})
            return {"new": False, "doc_name": doc_name, "chunks": len(existing["ids"])}

        pages      = self.processor.extract(pdf_path)
        chunks     = self.chunker.chunk(pages)
        texts      = [c.text for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        self.store.add_chunks(chunks, embeddings)

        return {
            "new":      True,
            "doc_name": doc_name,
            "pages":    len(pages),
            "chunks":   len(chunks),
        }

    def query(self, question: str, top_k: int = TOP_K, api_key: str = "") -> Dict:
        from google import genai

        if self.store.count() == 0:
            return {"answer": "⚠️ No documents indexed yet.", "sources": [], "retrieved_chunks": []}

        query_vec = self.embedder.embed_query(question)
        results   = self.store.search(query_vec, top_k=top_k)

        sections = []
        for i, c in enumerate(results, 1):
            sections.append(
                f"--- EXCERPT {i} ---\n"
                f"Document : {c.doc_name}  |  Page: {c.page_no}  |  Relevance: {c.score}\n"
                f"{c.text.strip()}"
            )
        context = "\n\n".join(sections)
        prompt  = (
            f"DOCUMENT EXCERPTS:\n\n{context}\n\n"
            f"{'=' * 60}\n\n"
            f"QUESTION: {question}\n\n"
            f"ANSWER (cite your sources):"
        )

        client   = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
        response = client.models.generate_content(
            model    = LLM_MODEL,
            contents = f"{SYSTEM_PROMPT}\n\n{prompt}",
            config   = {"temperature": 0.0},
        )

        return {
            "answer":           response.text,
            "sources":          [{"doc": r.doc_name, "page": r.page_no, "score": r.score} for r in results],
            "retrieved_chunks": [{"chunk_id": r.chunk_id, "doc_name": r.doc_name,
                                  "page_no": r.page_no, "text": r.text, "score": r.score}
                                 for r in results],
        }