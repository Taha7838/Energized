import logging
import hashlib
from datetime import datetime
from pathlib import Path
import os
import chromadb
import numpy as np
from core.settings import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load the embedding model ONCE at module level — same instance for
# both store and query operations. This guarantees consistent vectors.
# ---------------------------------------------------------------------------
# try:
#     _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
#     logger.info("[VectorStore] Embedding model loaded: all-MiniLM-L6-v2")
# except Exception as e:
#     import sys
#     print(f"\n[VectorStore] Failed to load embedding model: {e}\n")
#     sys.exit(1)


# def _embed(text: str) -> list[float]:
#     """Embed a single string. Returns a normalized float list."""
#     vec = _embed_model.encode(text, normalize_embeddings=True)
#     return vec.tolist()

_embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=os.environ["GEMINI_API_KEY"],
    task_type="SEMANTIC_SIMILARITY",
)

def _embed(text: str) -> list[float]:
    return _embeddings.embed_query(text)

# ==============================================================================

def _init_client() -> tuple[chromadb.PersistentClient, chromadb.Collection]:
    try:
        client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        logger.info(f"[ChromaDB] Connected. Store path: {settings.CHROMA_PERSIST_DIR}")
    except Exception as e:
        raise RuntimeError(
            f"[ChromaDB] Failed to initialize client at '{settings.CHROMA_PERSIST_DIR}': {e}"
        )

    try:
        # No embedding_function — we supply embeddings manually every time.
        collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(
            f"[ChromaDB] Collection '{settings.CHROMA_COLLECTION_NAME}' ready. "
            f"Documents stored: {collection.count()}"
        )
        return client, collection
    except Exception as e:
        raise RuntimeError(
            f"[ChromaDB] Failed to get or create collection "
            f"'{settings.CHROMA_COLLECTION_NAME}': {e}"
        )


try:
    _client, _collection = _init_client()
except RuntimeError as e:
    import sys
    print(f"\n{e}\n")
    sys.exit(1)


def search_similar(query: str) -> dict | None:
    try:
        query_embedding = _embed(query)
        results = _collection.query(
            query_embeddings=[query_embedding],
            n_results=1,
            include=["documents", "metadatas", "distances"],
        )
    except Exception as e:
        logger.error(f"[ChromaDB] Search failed for query '{query}': {e}")
        return None

    if not results["ids"] or not results["ids"][0]:
        logger.info(f"[ChromaDB] No results found for query: '{query}'")
        return None

    distance = results["distances"][0][0]
    similarity = 1 - distance

    logger.info(
        f"[ChromaDB] Closest match similarity: {similarity:.4f} "
        f"(threshold: {settings.SIMILARITY_THRESHOLD})"
    )

    if similarity < settings.SIMILARITY_THRESHOLD:
        logger.info("[ChromaDB] Similarity below threshold — cache miss.")
        return None

    metadata = results["metadatas"][0][0]
    document = results["documents"][0][0]

    logger.info(
        f"[ChromaDB] Cache HIT — returning cached result for: "
        f"'{metadata.get('query', 'unknown')}'"
    )

    return {
        "query": metadata.get("query", query),
        "summary": document,
        "sources": metadata.get("sources", "").split("||"),
        "timestamp": metadata.get("timestamp", ""),
        "from_cache": True,
    }


def store_result(query: str, summary: str, sources: list[str]) -> None:
    doc_id = hashlib.md5(query.lower().strip().encode()).hexdigest()
    timestamp = datetime.utcnow().isoformat()
    embedding = _embed(query)

    try:
        existing = _collection.get(ids=[doc_id])
        if existing["ids"]:
            _collection.update(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[summary],
                metadatas=[{
                    "query": query,
                    "sources": "||".join(sources),
                    "timestamp": timestamp,
                }],
            )
            logger.info(f"[ChromaDB] Updated existing entry for query: '{query}'")
        else:
            _collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[summary],
                metadatas=[{
                    "query": query,
                    "sources": "||".join(sources),
                    "timestamp": timestamp,
                }],
            )
            logger.info(f"[ChromaDB] Stored new result for query: '{query}'")

    except Exception as e:
        logger.error(f"[ChromaDB] Failed to store result for '{query}': {e}")


def get_all_history() -> list[dict]:
    try:
        count = _collection.count()
        if count == 0:
            return []

        results = _collection.get(include=["documents", "metadatas"])

        items = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            items.append({
                "query": meta.get("query", ""),
                "summary": doc,
                "sources": meta.get("sources", "").split("||"),
                "timestamp": meta.get("timestamp", ""),
                "from_cache": False,
            })

        items.sort(key=lambda x: x["timestamp"], reverse=True)
        return items

    except Exception as e:
        logger.error(f"[ChromaDB] Failed to retrieve history: {e}")
        return []