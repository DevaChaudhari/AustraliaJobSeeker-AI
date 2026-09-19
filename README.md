# Australia Job Seeker AI

AI-powered job search assistant for visa-friendly jobs in Australia. It searches SEEK, checks each ad against your visa type, ranks jobs against your resume, and generates tailored resumes and cover letters.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![LangChain](https://img.shields.io/badge/LangChain-Integration-green) ![LangGraph](https://img.shields.io/badge/LangGraph-Agents-brightgreen)

## Features

- **Visa-aware search**: flags citizen-only, clearance and PR-only roles for visas 500, 485, 482 and PR
- **Job ranking**: scores jobs on visa fit, skill match and role relevance
- **Resume tailoring and cover letters**: generated with Groq-hosted LLMs
- **Multiple interfaces**: REST API (FastAPI), A2A server and MCP server

## Architecture

```
POST /search-jobs
      │
      ▼
LangGraph pipeline:  search (Playwright / SEEK) → enrich (full job ads) → visa check
      │
      ▼
rank_jobs (visa fit + resume skill match) → response
```

## Project structure

```
.
├── src/australiajobseeker/
│   ├── agents/            # Visa, ranking, profile, resume, cover letter agents and the LangGraph pipeline
│   ├── scrapers/          # Playwright scrapers for SEEK
│   ├── api/               # FastAPI application
│   ├── a2a_server/        # A2A protocol server and client
│   ├── mcp_server/        # FastMCP server
│   ├── resources/         # Bundled sample resume
│   └── observability.py   # LangSmith tracing config
├── tests/                 # Offline pytest suite
├── docs/                  # A2A and MCP guides
├── examples/              # Example MCP client
├── deploy/kubernetes/     # Kubernetes manifests
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

## Getting started

Requires Python 3.10+ and a free [Groq API key](https://console.groq.com).

```bash
uv sync
uv run playwright install chromium
cp .env.example .env          # then set GROQ_API_KEY
uv run uvicorn australiajobseeker.api.main:app --reload
```

The API is at http://localhost:8000 (interactive docs at `/docs`). Without `uv`: `pip install -e .`.

### API

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `POST /search-jobs` | Body: `role`, `location`, `visa_type`, optional `resume_text` |
| `POST /generate-resume` | Body: `job_description`, optional `resume_text` |
| `POST /generate-cover-letter` | Body: `job_description`, `company`, `title`, optional `resume_text` |

### Other servers

```bash
uv run python -m australiajobseeker.a2a_server.main   # A2A server on :9999
```

See [docs/a2a-server.md](docs/a2a-server.md) and [docs/mcp.md](docs/mcp.md).

## Configuration

Set in `.env` (see [.env.example](.env.example)).

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | required | Groq API key |
| `SEEK_MAX_PAGES` | 1 | SEEK result pages to scrape |
| `SEEK_MAX_JOBS` | 10 | Jobs to scrape per search |
| `SEEK_PAGE_WAIT_MS` | 3000 | Wait after loading a results page |
| `JOB_DETAIL_WAIT_MS` | 2000 | Wait after loading a job page |
| `MAX_RESPONSE_JOBS` | 10 | Jobs returned by `/search-jobs` |
| `LANGSMITH_TRACING` | false | Enable LangSmith tracing (needs `LANGSMITH_API_KEY`) |
| `LANGSMITH_PROJECT` | | LangSmith project name |
| `PORT` | 8000 | API port in the Docker image |

## Testing

```bash
uv run pytest
```

Tests run offline; no API key or network is needed.

## Deployment

**Docker Compose** (API on :8000, A2A on :9999):

```bash
docker compose up --build
```

**Kubernetes**: see [deploy/kubernetes/README.md](deploy/kubernetes/README.md).

## Tech stack

LangChain and LangGraph, Groq (Llama 3.1), FastAPI, Playwright, A2A SDK, FastMCP, LangSmith.
