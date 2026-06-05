FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
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
RUN pip install --no-cache-dir -e .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose ports
EXPOSE 9999 8000 8501

# Run the A2A server by default
CMD ["python", "-m", "A2A.main"]
