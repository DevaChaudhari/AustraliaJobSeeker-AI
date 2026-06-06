# AustraliaJobSeeker AI

AI-powered job search platform for international students and visa holders in Australia. Filters real-time Seek jobs by visa type, checks eligibility from the actual job description, ranks jobs against your resume, and generates a tailored resume and cover letter in seconds.

Live Demo: https://australiajobseeker-frontend-952176467939.us-central1.run.app/

---

## The Problem

Seek.com has no visa filter. As an international student on a Student Visa (500), you waste hours reading job descriptions only to find "Australian Citizens Only" or "Must have full working rights" at the bottom.

This project solves that.

---

## Features

- Real-time job scraping from Seek using Playwright
- Visa eligibility filtering — supports Visa 500, 485, 482, PR
- Detects citizen-only, security clearance, and permanent resident restrictions from job descriptions
- Resume match scoring — ranks jobs by how well they match your resume
- AI-generated tailored resume in seconds for a specific job
- AI-generated cover letter in seconds for a specific company and role

---

## Tech Stack

### AI and Agents
- LangGraph — multi-agent pipeline (search, enrich, visa check, rank, generate)
- Groq LLM (Llama 3.1) — resume and cover letter generation
- LangSmith — real-time agent observability and tracing

### MCP and A2A
- Custom MCP (Model Context Protocol) servers — exposes job search, visa check, resume tailoring, and cover letter generation as callable tools for any AI agent
- A2A (Agent-to-Agent) servers — agents discover and call each other's skills directly for true multi-agent collaboration

### Backend
- FastAPI
- Python 3.10
- Playwright for web scraping

### Infrastructure
- Docker — fully containerized
- Kubernetes — production-grade orchestration with deployments, services, ingress, configmaps, and persistent volumes
- Google Cloud Run — serverless deployment
- Google Cloud Build — CI/CD pipeline, every git push auto-builds and deploys

---

## Project Structure

```
AustraliaJobSeeker-AI/
├── agents/              # LangGraph agents (visa, resume, cover letter, ranking, routing)
├── api/                 # FastAPI backend
├── frontend/            # Frontend application
├── MCP/                 # MCP servers and client
├── A2A/                 # A2A agent server
├── Langsmith/           # LangSmith tracing integration
├── tools/               # Seek scraper, job enrichment tools
├── data/                # Sample resume and generated outputs
├── kubernetes/          # Kubernetes manifests
├── Docker/              # Docker configuration
├── Dockerfile           # Main Dockerfile
├── cloudbuild.yaml      # CI/CD pipeline config
└── requirements.txt
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Service status |
| POST | `/search-jobs` | Search and filter jobs by visa type |
| POST | `/generate-resume` | Generate a tailored resume for a job |
| POST | `/generate-cover-letter` | Generate a cover letter for a job |

### Example — Generate Resume

```bash
curl -X POST https://australiajobseeker-ai-952176467939.us-central1.run.app/generate-resume \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Python developer with FastAPI experience..."
  }'
```

### Example — Generate Cover Letter

```bash
curl -X POST https://australiajobseeker-ai-952176467939.us-central1.run.app/generate-cover-letter \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Python developer...",
    "company": "Tech Solutions Australia",
    "title": "Python Developer"
  }'
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GROQ_API_KEY` | Groq API key for LLM |
| `LANGSMITH_API_KEY` | LangSmith API key for tracing |
| `LANGSMITH_TRACING` | Set to `true` to enable tracing |
| `LANGSMITH_PROJECT` | LangSmith project name |
| `MAX_RESPONSE_JOBS` | Max jobs to return (default: 10) |

---

## Local Setup

```bash
# Clone the repo
git clone https://github.com/DevaChaudhari/AustraliaJobSeeker-AI.git
cd AustraliaJobSeeker-AI

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set environment variables
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run the backend
uvicorn api.main:app --host 0.0.0.0 --port 8080
```

---

## Deployment

The project uses Google Cloud Build for CI/CD. Every push to `main` automatically builds the Docker image and deploys to Cloud Run.

```bash
# Manual deploy
gcloud run deploy australiajobseeker-ai \
  --region=us-central1 \
  --memory=2Gi \
  --set-env-vars=GROQ_API_KEY=your_key
```

---

## Author

Devendra Chaudhari
GitHub: https://github.com/DevaChaudhari
