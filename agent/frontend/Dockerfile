# ─── Frontend — Dockerfile ───────────────────────────────────────────────────
# React + Vite frontend, served via nginx.
# Listens on port 80.
# ─────────────────────────────────────────────────────────────────────────────

# Stage 1: Node build
FROM node:20-alpine AS builder

WORKDIR /app

# Copy lockfile first for better layer caching
COPY package.json package-lock.json ./
RUN npm ci --prefer-offline

# Copy source and build
COPY . .
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: nginx runtime (tiny — ~25 MB)
FROM nginx:1.27-alpine AS runtime

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy Vite build output
COPY --from=builder /app/dist /usr/share/nginx/html

# nginx config: proxy /api → agent backend, /rag/api → rag backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
