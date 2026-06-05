FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl wget gnupg \
    libnss3 libatk-bridge2.0-0 \
    libdrm2 libxkbcommon0 libgbm1 \
    libasound2 libxshmfence1 libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

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

RUN pip install --no-cache-dir -e .
RUN playwright install chromium

ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]