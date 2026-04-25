# backend/main.py
import asyncio
import json
import logging
import queue
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from core.settings import settings
from memory.vector_store import search_similar, get_all_history
from schemas.models import QueryRequest, ResearchResult, HistoryResponse, HistoryItem
from utils.file_writer import append_to_knowledge_base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("Energy Researcher Agent — Backend Starting")
    logger.info(f"  LLM Model     : {settings.GEMINI_MODEL}")
    logger.info(f"  Cache Threshold: {settings.SIMILARITY_THRESHOLD}")
    logger.info(f"  Chroma Store  : {settings.CHROMA_PERSIST_DIR}")
    logger.info(f"  Knowledge Base: {settings.KNOWLEDGE_BASE_PATH}")
    logger.info(f"  Frontend URL  : {settings.FRONTEND_URL}")
    logger.info("=" * 60)
    yield
    logger.info("Energy Researcher Agent — Backend Shutting Down")


app = FastAPI(
    title="Energy Researcher Agent",
    description="LLM-powered autonomous research agent for the energy industry.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# POST /api/v1/query  — synchronous, returns full result (cache or live)
# ---------------------------------------------------------------------------

@app.post("/api/v1/query", response_model=ResearchResult)
async def query_endpoint(request: QueryRequest) -> ResearchResult:
    """
    Non-streaming research endpoint.
    Checks semantic cache first. Runs crew on cache miss.
    Use /api/v1/query/stream for real-time SSE output.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    logger.info(f"[POST /query] Received: '{query}'")

    # Cache check
    cached = search_similar(query)
    if cached:
        logger.info(f"[POST /query] Cache HIT — returning cached result.")
        try:
            append_to_knowledge_base(
                query=cached["query"],
                summary=cached["summary"],
                sources=cached["sources"],
                from_cache=True,
            )
        except Exception as e:
            logger.warning(f"[POST /query] Failed to log cache hit to file: {e}")

        return ResearchResult(**cached)

    # Cache miss — run crew in thread pool (it's blocking)
    logger.info(f"[POST /query] Cache MISS — running crew.")
    try:
        loop = asyncio.get_event_loop()
        from crew.runner import run_research_crew

        result = await loop.run_in_executor(
            None, lambda: run_research_crew(query=query, stream_queue=None)
        )
        return ResearchResult(**result)

    except RuntimeError as e:
        logger.error(f"[POST /query] Crew failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# GET /api/v1/query/stream  — SSE streaming endpoint
# ---------------------------------------------------------------------------

@app.get("/api/v1/query/stream")
async def query_stream_endpoint(q: str):
    """
    SSE streaming endpoint. Emits:
      - event: 'progress'  → intermediate agent thoughts (string)
      - event: 'result'    → final JSON result
      - event: 'error'     → error message string
      - event: 'done'      → signals stream end
    """
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")

    logger.info(f"[SSE /stream] Connected for query: '{query}'")

    async def event_generator():
        # Check cache first — no streaming needed for cache hits
        cached = search_similar(query)
        if cached:
            logger.info(f"[SSE /stream] Cache HIT.")
            try:
                append_to_knowledge_base(
                    query=cached["query"],
                    summary=cached["summary"],
                    sources=cached["sources"],
                    from_cache=True,
                )
            except Exception as e:
                logger.warning(f"[SSE /stream] Failed to log cache hit to file: {e}")

            yield {
                "event": "progress",
                "data": "⚡ Found cached result — returning instantly.",
            }
            yield {
                "event": "result",
                "data": json.dumps(cached),
            }
            yield {"event": "done", "data": ""}
            return

        # Cache miss — set up streaming queue and run crew in background thread
        stream_q: queue.Queue = queue.Queue()
        result_holder: dict = {}
        error_holder: dict = {}

        def _run_crew():
            try:
                from crew.runner import run_research_crew
                result = run_research_crew(query=query, stream_queue=stream_q)
                result_holder["data"] = result
            except Exception as e:
                error_holder["error"] = str(e)
            finally:
                stream_q.put(None)  # sentinel — signals stream end

        thread = threading.Thread(target=_run_crew, daemon=True)
        thread.start()

        # Drain the queue and emit SSE events
        while True:
            try:
                # Non-blocking get with short timeout so we stay responsive
                msg = stream_q.get(timeout=0.1)
            except queue.Empty:
                # Keep connection alive while crew is running
                if not thread.is_alive() and stream_q.empty():
                    break
                await asyncio.sleep(0.05)
                continue

            if msg is None:  # sentinel received
                break

            yield {
                "event": "progress",
                "data": msg,
            }
            await asyncio.sleep(0)  # yield control back to event loop

        thread.join(timeout=5)

        if error_holder:
            logger.error(f"[SSE /stream] Crew error: {error_holder['error']}")
            yield {
                "event": "error",
                "data": error_holder["error"],
            }
        elif result_holder:
            yield {
                "event": "result",
                "data": json.dumps(result_holder["data"]),
            }
        else:
            yield {
                "event": "error",
                "data": "Crew completed but returned no result.",
            }

        yield {"event": "done", "data": ""}
        logger.info(f"[SSE /stream] Stream complete for: '{query}'")

    return EventSourceResponse(event_generator())


# ---------------------------------------------------------------------------
# GET /api/v1/history
# ---------------------------------------------------------------------------

@app.get("/api/v1/history", response_model=HistoryResponse)
async def history_endpoint() -> HistoryResponse:
    """Returns all past research results from ChromaDB, newest first."""
    try:
        items = get_all_history()
        return HistoryResponse(items=[HistoryItem(**item) for item in items])
    except Exception as e:
        logger.error(f"[GET /history] Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {e}")


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok", "model": settings.GEMINI_MODEL}