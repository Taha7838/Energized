# ─── Agent Backend — Dockerfile ──────────────────────────────────────────────
# FastAPI + CrewAI multi-agent researcher backend.
# Listens on port 8000.
# ─────────────────────────────────────────────────────────────────────────────

# Stage 1: dependency builder (keeps final image lean)
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools required by some Python packages (e.g. chromadb, grpcio)
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

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY . .

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

# Graceful shutdown: uvicorn handles SIGTERM properly
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
