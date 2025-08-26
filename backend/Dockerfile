FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

# Work inside backend so "main:app" can import cleanly
WORKDIR /app/backend

# Install Python deps first for better caching
COPY requirements.txt .
# Pin aiohttp to avoid accidental major bumps
RUN pip install --no-cache-dir -r requirements.txt aiohttp==3.9.5

# Copy backend code
COPY . .

# Copy frontend so FastAPI can serve it
COPY ../frontend /app/frontend

# Runtime
ENV PORT=8000
EXPOSE 8000

# Production server (Gunicorn + Uvicorn workers)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000", "--log-level", "info", "--timeout", "60", "--workers", "2"]