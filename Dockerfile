FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (minimal for Cloud Run)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget gnupg \
    libnss3 libatk-bridge2.0-0 \
    libdrm2 libxkbcommon0 libgbm1 \
    libasound2 libxshmfence1 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock ./
COPY agents/ ./agents/
COPY tools/ ./tools/
COPY models/ ./models/
COPY A2A/ ./A2A/
COPY Langsmith/ ./Langsmith/
COPY MCP/ ./MCP/
COPY api/ ./api/
COPY frontend/ ./frontend/
COPY data/ ./data/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# Install playwright browsers
RUN playwright install chromium

# Set Python path
ENV PYTHONPATH=/app:$PYTHONPATH

# Cloud Run expects the container to listen on port 8080
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the backend API server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
