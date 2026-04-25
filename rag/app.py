import streamlit as st
import os, re, uuid, tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict

st.set_page_config(
    page_title="EnergyRAG",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Playfair+Display:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:#09090f; --surface:#111118; --surface2:#18181f; --surface3:#1e1e28;
    --border:#272733; --border2:#32323f; --amber:#f59e0b;
    --amber-glow:rgba(245,158,11,0.15); --red:#ef4444; --green:#22c55e;
    --text:#f1f0ee; --text2:#a8a7b0; --text3:#5c5b68;
}
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{
    font-family:'Outfit',sans-serif !important;
    background:var(--bg) !important; color:var(--text) !important;}
footer,.stDeployButton{display:none !important;}
#MainMenu{visibility:hidden !important;}
.block-container{padding:0 !important; max-width:100% !important;}
.main > div{padding:0 !important;}

/* ── Auto-center content when sidebar collapses ── */
/* Streamlit's section.main already fills all available horizontal space
   (it shrinks when sidebar opens, grows when it closes).
   We constrain the inner content to max 860px and auto-center it.
   This means: sidebar open = full width content, sidebar closed = centered column. */

section[data-testid="stMain"] > div:first-child {
    max-width: 100% !important;
    margin: 0 !important;
}

/* Inner block container — this is what we center */
div[data-testid="stMainBlockContainer"],
div.stMainBlockContainer {
    max-width: 860px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    width: 100% !important;
    transition: max-width 0.25s ease !important;
}

/* When sidebar is expanded, allow full width again */
[data-testid="stAppViewContainer"]:has(
    [data-testid="stSidebar"][aria-expanded="true"]
) div[data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"]{
    background:var(--surface) !important;
    border-right:1px solid var(--border) !important;
    /* NO min-width/max-width — let Streamlit control sidebar width natively.
       Setting these prevents the sidebar from collapsing to 0 properly. */
}
[data-testid="stSidebar"]>div:first-child{padding:0 !important; background:var(--surface) !important;}
[data-testid="stSidebar"] section{background:var(--surface) !important;}
[data-testid="stSidebar"] ::-webkit-scrollbar{width:3px;}
[data-testid="stSidebar"] ::-webkit-scrollbar-thumb{background:var(--border2);border-radius:2px;}

/* ── Collapsed sidebar tab — always visible ── */
[data-testid="stSidebarCollapsedControl"]{
    display:flex !important; visibility:visible !important; opacity:1 !important;
    background:var(--surface) !important; border-right:1px solid var(--border) !important;}
[data-testid="stSidebarCollapsedControl"] button{
    display:flex !important; visibility:visible !important; opacity:1 !important;
    background:transparent !important; border:none !important;}
[data-testid="stSidebarCollapsedControl"] svg{
    fill:var(--amber) !important; color:var(--amber) !important;}

/* ── Inputs ── */
input[type="text"],input[type="password"],textarea{
    background:var(--surface3) !important; border:1px solid var(--border2) !important;
    border-radius:8px !important; color:var(--text) !important;
    font-family:'Outfit',sans-serif !important; font-size:14px !important;}
input:focus,textarea:focus{
    border-color:var(--amber) !important; box-shadow:0 0 0 3px var(--amber-glow) !important;}

/* ── Chat input bar ── */
[data-testid="stChatInput"]{
    background:var(--surface) !important; border-top:1px solid var(--border) !important;
    padding:16px 32px 20px !important;}
[data-testid="stChatInput"] textarea{
    background:var(--surface3) !important; border:1px solid var(--border2) !important;
    border-radius:12px !important; font-size:15px !important; color:var(--text) !important;}
[data-testid="stChatInput"] textarea:focus{
    border-color:var(--amber) !important; box-shadow:0 0 0 3px var(--amber-glow) !important;}
[data-testid="stChatInput"] button{
    background:var(--amber) !important; border-radius:10px !important;
    border:none !important; color:#09090f !important;}

/* ── Buttons ── */
.stButton>button{
    background:var(--surface3) !important; color:var(--text2) !important;
    border:1px solid var(--border2) !important; border-radius:8px !important;
    font-family:'Outfit',sans-serif !important; font-size:13px !important;
    font-weight:500 !important; padding:8px 14px !important;
    transition:all 0.18s !important; width:100% !important;}
.stButton>button:hover{border-color:var(--amber) !important; color:var(--amber) !important;}
.danger-btn .stButton>button{
    background:rgba(239,68,68,0.07) !important; color:#ef4444 !important;
    border-color:rgba(239,68,68,0.2) !important; font-size:11px !important;
    padding:5px 10px !important; width:auto !important;}
.danger-btn .stButton>button:hover{
    background:rgba(239,68,68,0.15) !important; border-color:#ef4444 !important;}
.sug-btn .stButton>button{
    background:var(--surface2) !important; border:1px solid var(--border) !important;
    border-radius:20px !important; color:var(--text2) !important;
    font-size:13px !important; padding:8px 16px !important; width:auto !important;}
.sug-btn .stButton>button:hover{
    border-color:var(--amber) !important; color:var(--amber) !important;
    background:var(--amber-glow) !important;}

/* ── File uploader ── */
[data-testid="stFileUploader"]{
    background:var(--surface3) !important;
    border:1.5px dashed var(--border2) !important; border-radius:12px !important;}
[data-testid="stFileUploader"]:hover{border-color:var(--amber) !important;}
[data-testid="stFileUploaderDropzone"]{background:transparent !important; padding:16px !important;}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span{color:var(--text3) !important; font-size:13px !important;}

/* ── Misc ── */
[data-testid="stToggle"] label,[data-testid="stSlider"] p{color:var(--text2) !important; font-size:13px !important;}
[data-testid="stExpander"]{background:var(--surface2) !important; border:1px solid var(--border) !important; border-radius:8px !important; margin:6px 0 !important;}
[data-testid="stExpander"] summary{color:var(--text3) !important; font-size:12px !important;}
.stSuccess{background:rgba(34,197,94,0.08) !important; border-color:var(--green) !important;}
.stError{background:rgba(239,68,68,0.08) !important; border-color:var(--red) !important;}
.stInfo{background:var(--amber-glow) !important; border-color:var(--amber) !important;}
[data-testid="stAlert"]{border-radius:8px !important; font-size:13px !important;}
.stSpinner>div{border-top-color:var(--amber) !important;}
::-webkit-scrollbar{width:4px; height:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border2); border-radius:2px;}
label{color:var(--text3) !important; font-size:11px !important; font-weight:600 !important;
      text-transform:uppercase !important; letter-spacing:0.8px !important;}
hr{border-color:var(--border) !important; margin:10px 0 !important;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  DATA CLASSES  (identical to notebook)
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
#  CONFIG  (mirrors notebook constants)
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
#  PIPELINE CLASSES  (exact copy from notebook)
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
                    pages.append(Page(page_no=i+1, text=cleaned, doc_name=doc_name))
        return pages

    def _clean(self, text: str) -> str:
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]{3,}", " ", text)
        text = re.sub(r"(?i)page\s+\d+", "", text)
        return text.strip()


class TextChunker:
    """Sliding-window token-based chunker — identical to notebook."""

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
                        page_no=page.page_no, text=chunk_text, token_count=end-start))
                if end == len(tokens):
                    break
        return all_chunks


class GeminiEmbedder:
    """Local sentence-transformers embedder — identical to notebook."""

    def __init__(self, model: str = EMBEDDING_MODEL):
        from sentence_transformers import SentenceTransformer
        self.model_name = model
        self._model     = SentenceTransformer(model)

    def embed_texts(self, texts: List[str], show_progress: bool = False) -> List[List[float]]:
        return self._model.encode(
            texts,
            show_progress_bar    = show_progress,
            convert_to_numpy     = True,
            normalize_embeddings = True,
        ).tolist()

    def embed_query(self, query: str) -> List[float]:
        return self._model.encode(
            query,
            convert_to_numpy     = True,
            normalize_embeddings = True,
        ).tolist()


class VectorStore:
    """ChromaDB-backed persistent vector store — identical to notebook."""

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
            metadatas  = [{"doc_name": c.doc_name, "page_no": c.page_no,
                           "token_count": c.token_count} for c in chunks],
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
                chunk_id=cid, doc_name=meta["doc_name"], page_no=meta["page_no"],
                text=results["documents"][0][i],
                score=round(1 - results["distances"][0][i], 4),
            ))
        return out

    def list_documents(self) -> List[str]:
        if self._col.count() == 0:
            return []
        return sorted(set(m["doc_name"] for m in self._col.get(include=["metadatas"])["metadatas"]))

    def delete_document(self, doc_name: str) -> None:
        self._col.delete(where={"doc_name": doc_name})

    def count(self) -> int:
        return self._col.count()


class RAGChain:
    """
    Orchestrates the full RAG pipeline — identical logic to the notebook.
    PDF → Chunks → Embeddings → VectorDB → Retrieval → Gemini → Answer
    """

    def __init__(self):
        self.processor = PDFProcessor()
        self.chunker   = TextChunker()
        self.embedder  = GeminiEmbedder()
        self.store     = VectorStore()

    def ingest(self, pdf_path: str) -> Dict:
        """Ingest a PDF: extract → chunk → embed → store."""
        doc_name = Path(pdf_path).stem

        # Skip if already indexed
        if doc_name in self.store.list_documents():
            existing = self.store._col.get(where={"doc_name": doc_name})
            return {"new": False, "doc_name": doc_name, "chunks": len(existing["ids"])}

        pages      = self.processor.extract(pdf_path)
        chunks     = self.chunker.chunk(pages)
        texts      = [c.text for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        self.store.add_chunks(chunks, embeddings)

        return {"new": True, "doc_name": doc_name,
                "pages": len(pages), "chunks": len(chunks)}

    def query(self, question: str, top_k: int = TOP_K, api_key: str = "") -> Dict:
        """Answer a question using retrieved context + Gemini."""
        from google import genai

        if self.store.count() == 0:
            return {"answer": "⚠️ No documents indexed yet.", "sources": [], "retrieved_chunks": []}

        # 1 — Embed question
        query_vec = self.embedder.embed_query(question)

        # 2 — Retrieve
        results = self.store.search(query_vec, top_k=top_k)

        # 3 — Build prompt (exact same as notebook)
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
            f"{'='*60}\n\n"
            f"QUESTION: {question}\n\n"
            f"ANSWER (cite your sources):"
        )

        # 4 — Generate with Gemini (same call as notebook)
        client   = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
        response = client.models.generate_content(
            model    = LLM_MODEL,
            contents = f"{SYSTEM_PROMPT}\n\n{prompt}",
            config   = {"temperature": 0.0},
        )

        return {
            "answer":            response.text,
            "sources":           [{"doc": r.doc_name, "page": r.page_no, "score": r.score} for r in results],
            "retrieved_chunks":  results,
        }


# ─────────────────────────────────────────────────────────────────
#  CACHED SINGLETON  (one RAGChain per Streamlit session)
# ─────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_rag() -> RAGChain:
    return RAGChain()


# ─────────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────────
if "messages"  not in st.session_state: st.session_state.messages  = []
if "pending_q" not in st.session_state: st.session_state.pending_q = None


# ─────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 20px 18px;border-bottom:1px solid #272733;">
      <div style="display:flex;align-items:center;gap:10px;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#f59e0b,#d97706);
                    border-radius:10px;display:flex;align-items:center;justify-content:center;
                    font-size:17px;box-shadow:0 2px 10px rgba(245,158,11,0.35);">⚡</div>
        <div>
          <div style="font-family:'Playfair Display',serif;font-size:17px;font-weight:800;
                      color:#f1f0ee;letter-spacing:-0.3px;">EnergyRAG</div>
          <div style="font-size:11px;color:#5c5b68;">Document Intelligence</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── API Key
    st.markdown("**🔑 Gemini API Key**")
    api_key = st.text_input("api_key", type="password",
                            placeholder="AIza...", label_visibility="collapsed")
    if api_key:
        st.success("✓ Key configured")
    else:
        st.caption("Free key → [aistudio.google.com](https://aistudio.google.com/app/apikey)")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Upload
    st.markdown("**📄 Upload Documents**")
    uploaded_files = st.file_uploader(
        "upload", type=["pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )
    if uploaded_files:
        rag = get_rag()
        for f in uploaded_files:
            tmp = Path(tempfile.mkdtemp()) / f.name
            tmp.write_bytes(f.getvalue())
            with st.spinner(f"Indexing {f.name}…"):
                try:
                    r = rag.ingest(str(tmp))
                    if r["new"]:
                        st.success(f"✓ {r['pages']} pages · {r['chunks']} chunks")
                    else:
                        st.info(f"Already indexed · {r['chunks']} chunks")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Indexed docs
    rag  = get_rag()
    docs = rag.store.list_documents()
    if docs:
        st.markdown("**📚 Indexed Documents**")
        for doc in docs:
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f'<div style="background:#18181f;border:1px solid #272733;border-radius:7px;'
                    f'padding:7px 11px;font-size:13px;color:#a8a7b0;overflow:hidden;'
                    f'text-overflow:ellipsis;white-space:nowrap;" title="{doc}">📄 {doc}</div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
                if st.button("✕", key=f"del_{doc}"):
                    rag.store.delete_document(doc)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    # ── Settings
    st.markdown("**⚙️ Settings**")
    top_k         = st.slider("Context chunks (Top-K)", 3, 10, TOP_K)
    show_excerpts = st.toggle("Show source excerpts", value=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if st.session_state.messages:
        st.markdown('<div class="danger-btn">', unsafe_allow_html=True)
        if st.button("🗑  Clear conversation"):
            st.session_state.messages = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:20px;padding-top:12px;border-top:1px solid #272733;text-align:center;">
      <span style="font-size:10px;color:#5c5b68;">
        Gemini 2.5 Flash · sentence-transformers · ChromaDB
      </span>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  MAIN AREA
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:20px 36px 16px;border-bottom:1px solid #272733;background:#09090f;">
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div>
      <h1 style="font-family:'Playfair Display',serif;font-size:22px;font-weight:800;
                 color:#f1f0ee;margin:0;letter-spacing:-0.5px;">Document Q&amp;A</h1>
      <p style="font-size:13px;color:#5c5b68;margin:3px 0 0;">
        Answers grounded strictly in your uploaded energy documents
      </p>
    </div>
    <div style="display:flex;align-items:center;gap:8px;">
      <div style="width:8px;height:8px;border-radius:50%;background:#22c55e;
                  box-shadow:0 0 6px #22c55e;"></div>
      <span style="font-size:12px;color:#5c5b68;font-family:'JetBrains Mono',monospace;">
        RAG active
      </span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Empty state
if not st.session_state.messages:
    rag      = get_rag()
    docs_now = rag.store.list_documents()

    if not docs_now:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    padding:90px 40px;text-align:center;">
          <div style="width:68px;height:68px;background:linear-gradient(135deg,#f59e0b22,#d9770622);
                      border:1px solid #f59e0b33;border-radius:18px;display:flex;align-items:center;
                      justify-content:center;font-size:30px;margin-bottom:22px;">📄</div>
          <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:800;
                     color:#f1f0ee;margin:0 0 10px;">Upload a document to begin</h2>
          <p style="font-size:14px;color:#5c5b68;max-width:360px;line-height:1.7;margin:0 0 28px;">
            Use the sidebar to upload any energy PDF — reports, manuals, filings.
            Ask questions and get precise cited answers.
          </p>
          <div style="display:flex;gap:10px;flex-wrap:wrap;justify-content:center;">
            <div style="padding:8px 16px;background:#18181f;border:1px solid #272733;
                        border-radius:20px;font-size:13px;color:#5c5b68;">📊 Operational reports</div>
            <div style="padding:8px 16px;background:#18181f;border:1px solid #272733;
                        border-radius:20px;font-size:13px;color:#5c5b68;">🔧 Equipment manuals</div>
            <div style="padding:8px 16px;background:#18181f;border:1px solid #272733;
                        border-radius:20px;font-size:13px;color:#5c5b68;">📋 Safety filings</div>
          </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;
                    padding:50px 40px 20px;text-align:center;">
          <div style="width:58px;height:58px;background:linear-gradient(135deg,#f59e0b,#d97706);
                      border-radius:16px;display:flex;align-items:center;justify-content:center;
                      font-size:26px;margin-bottom:18px;box-shadow:0 4px 20px rgba(245,158,11,0.3);">⚡</div>
          <h2 style="font-family:'Playfair Display',serif;font-size:24px;font-weight:800;
                     color:#f1f0ee;margin:0 0 8px;">
            {len(docs_now)} document{'s' if len(docs_now)>1 else ''} ready
          </h2>
          <p style="font-size:14px;color:#5c5b68;margin:0 0 28px;">
            Ask anything — every answer is cited to its source page
          </p>
        </div>""", unsafe_allow_html=True)

        suggestions = [
            "Summarise the key findings",
            "What safety protocols are mentioned?",
            "What are the main production figures?",
            "What environmental commitments are described?",
            "What capital projects are planned?",
            "What regulatory requirements apply?",
        ]
        cols = st.columns(3)
        for i, s in enumerate(suggestions):
            with cols[i % 3]:
                st.markdown('<div class="sug-btn">', unsafe_allow_html=True)
                if st.button(s, key=f"sug_{i}"):
                    st.session_state.pending_q = s
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)


# ── Chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;padding:12px 36px 4px;gap:10px;">
          <div style="max-width:72%;background:#1e1e28;border:1px solid #272733;
                      border-radius:20px 20px 6px 20px;padding:13px 17px;
                      font-size:15px;line-height:1.65;color:#f1f0ee;
                      box-shadow:0 2px 10px rgba(0,0,0,0.3);">
            {msg['content']}
          </div>
          <div style="width:32px;height:32px;border-radius:50%;background:#1e1e28;
                      border:1px solid #272733;display:flex;align-items:center;
                      justify-content:center;font-size:14px;flex-shrink:0;margin-top:2px;">👤</div>
        </div>""", unsafe_allow_html=True)
    else:
        answer  = msg.get("content", "")
        sources = msg.get("sources", [])
        chunks  = msg.get("chunks", [])
        is_err  = msg.get("error", False)
        border  = "#ef444444" if is_err else "#f59e0b33"
        left_b  = "#ef4444"   if is_err else "#f59e0b"

        st.markdown(f"""
        <div style="display:flex;padding:12px 36px 4px;gap:10px;align-items:flex-start;">
          <div style="width:32px;height:32px;border-radius:50%;
                      background:linear-gradient(135deg,#f59e0b,#d97706);
                      display:flex;align-items:center;justify-content:center;
                      font-size:14px;flex-shrink:0;margin-top:2px;
                      box-shadow:0 2px 8px rgba(245,158,11,0.3);">⚡</div>
          <div style="flex:1;max-width:80%;">
            <div style="background:#111118;border:1px solid {border};
                        border-left:3px solid {left_b};
                        border-radius:6px 20px 20px 20px;padding:15px 19px;
                        font-size:15px;line-height:1.75;color:#f1f0ee;
                        box-shadow:0 2px 14px rgba(0,0,0,0.35);">
              {answer.replace(chr(10), '<br>')}
            </div>
        """, unsafe_allow_html=True)

        if sources and not is_err:
            pills = "".join([
                f'<span style="display:inline-flex;align-items:center;gap:4px;background:#18181f;'
                f'border:1px solid #272733;border-radius:20px;padding:3px 10px;font-size:11px;'
                f'color:#a8a7b0;font-family:\'JetBrains Mono\',monospace;margin:3px 3px 0 0;">'
                f'📄 {s["doc"]} · p.{s["page"]} <span style="color:#f59e0b;">{s["score"]:.2f}</span></span>'
                for s in sources
            ])
            st.markdown(f'<div style="margin-top:9px;display:flex;flex-wrap:wrap;">{pills}</div>',
                        unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)

        if show_excerpts and chunks and not is_err:
            with st.expander(f"📖 View {len(chunks)} source excerpts", expanded=False):
                for i, ch in enumerate(chunks, 1):
                    st.markdown(f"""
                    <div style="background:#18181f;border:1px solid #272733;
                                border-left:2px solid #f59e0b44;border-radius:8px;
                                padding:11px 14px;margin-bottom:8px;">
                      <div style="font-size:10px;color:#f59e0b;font-family:'JetBrains Mono',monospace;
                                  font-weight:500;margin-bottom:7px;text-transform:uppercase;letter-spacing:0.5px;">
                        [{i}] {ch.doc_name} · Page {ch.page_no} · Score {ch.score:.3f}
                      </div>
                      <div style="font-size:13px;color:#5c5b68;line-height:1.65;">
                        {ch.text[:450]}{'…' if len(ch.text)>450 else ''}
                      </div>
                    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
#  CHAT INPUT
# ─────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask anything about your energy documents…")
question   = user_input or st.session_state.pending_q
if st.session_state.pending_q:
    st.session_state.pending_q = None

if question:
    if not api_key:
        st.error("⚠️ Enter your Gemini API key in the sidebar first.")
        st.stop()

    rag = get_rag()
    if rag.store.count() == 0:
        st.error("⚠️ Upload at least one PDF in the sidebar first.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": question})

    with st.spinner("Thinking…"):
        try:
            result = rag.query(question, top_k=top_k, api_key=api_key)
            st.session_state.messages.append({
                "role":    "assistant",
                "content": result["answer"],
                "sources": result["sources"],
                "chunks":  result["retrieved_chunks"],
                "error":   False,
            })
        except Exception as e:
            st.session_state.messages.append({
                "role":    "assistant",
                "content": f"Error: {e}",
                "sources": [], "chunks": [], "error": True,
            })
    st.rerun()
