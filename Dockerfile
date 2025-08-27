FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates tzdata && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first for better caching
COPY backend/requirements.txt .
# Pin aiohttp to avoid accidental major bumps
RUN pip install --no-cache-dir -r requirements.txt aiohttp==3.9.5

# Copy backend & frontend into image
COPY backend/ /app/backend
COPY frontend/ /app/frontend

# Env & port
ENV PORT=8000
EXPOSE 8000


# Run backend
WORKDIR /app/backend

# Use platform PORT if provided, else 8000
CMD ["bash","-lc","gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-8000} --log-level info --timeout 60 --workers 2"]