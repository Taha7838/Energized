# ─── RAG Backend — Dockerfile ────────────────────────────────────────────────
# FastAPI RAG backend: PDF ingestion, ChromaDB vector store, Gemini Q&A.
# Listens on port 8001.
# ─────────────────────────────────────────────────────────────────────────────

# Stage 1: dependency builder
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: lean runtime image
FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

# Copy application source (exclude chroma_db — mounted as volume at runtime)
COPY . .

# Persist ChromaDB data via a named volume (declared in docker-compose.yml)
VOLUME ["/app/chroma_db"]

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
