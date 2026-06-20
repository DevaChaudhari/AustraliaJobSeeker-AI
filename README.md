# Australia Job Seeker AI 🇦🇺

> AI-powered job search assistant for finding visa-friendly AI jobs in Australia with intelligent resume and cover letter generation.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![LangChain](https://img.shields.io/badge/LangChain-Integration-green) ![LangGraph](https://img.shields.io/badge/LangGraph-Agents-brightgreen) ![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red)

## 🎯 Overview

**AustraliaJobSeeker AI** is an intelligent job search and application assistant that helps users find and apply for AI jobs in Australia. It leverages:

- **LangGraph** for multi-agent orchestration
- **LangChain** for LLM integration (Groq API)
- **Streamlit** for an intuitive web interface
- **FastAPI** for a scalable backend
- **Playwright** for web scraping job listings
- **A2A Protocol** for agent capability exposure

### Key Features

✨ **Visa-Aware Job Search** - Filter jobs by visa eligibility (500, 485, 482, PR)  
🤖 **AI-Powered Resume Generation** - Tailor resumes to specific job descriptions  
📝 **Intelligent Cover Letter Writing** - Generate personalized cover letters  
🔍 **Job Description Analysis** - Extract and analyze key job requirements  
📊 **Job Ranking & Matching** - Score jobs based on profile fit  
🌐 **Multi-Agent Collaboration** - Supervisor agent coordinates specialized agents  
🚀 **Production-Grade Deployment** - Docker, Kubernetes, Google Cloud Run support

## 📁 Project Structure

```
AustraliaJobSeeker-AI/
├── agents/                      # LangGraph agent definitions
│   ├── supervisor_agent.py      # Main orchestrator agent
│   ├── router_agent.py          # Routes user queries to appropriate agents
│   ├── job_enrichment_agent.py  # Enriches job descriptions with analysis
│   ├── ranking_agent.py         # Ranks and scores jobs
│   ├── resume_agent.py          # Generates tailored resumes
│   ├── cover_letter_agent.py    # Generates cover letters
│   ├── profile_agent.py         # Manages user profiles
│   ├── visa_agent.py            # Handles visa eligibility checks
│   └── langgraph_supervisor.py  # Supervises agent workflow
├── tools/                       # Utility tools for scraping and data processing
│   ├── job_details_scraper.py   # Scrapes job details from listings
│   └── seek_scraper.py          # Scrapes Seek.com.au job listings
├── A2A/                         # A2A Protocol Server
│   ├── main.py                  # A2A server entry point
│   ├── agent_executor.py        # Executes agents via A2A interface
│   └── client.py                # A2A client implementation
├── api/                         # FastAPI backend
│   └── main.py                  # RESTful API endpoints
├── frontend/                    # Streamlit web application
│   ├── app.py                   # Main frontend entry point
│   ├── Dockerfile               # Frontend container image
│   └── requirements.txt          # Frontend-specific dependencies
├── models/                      # Pydantic data schemas
│   └── schemas.py               # Request/response schemas
├── MCP/                         # Model Context Protocol integration
│   ├── MCP_client/              # MCP client implementation
│   └── MCP_servers/             # MCP server setup
├── kubernetes/                  # K8s deployment manifests
├── Docker/                      # Docker compose configurations
├── tests/                       # Unit and integration tests
├── Langsmith/                   # LangSmith integration for monitoring
├── pyproject.toml               # Project configuration and dependencies
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Main application Dockerfile
├── docker-compose.yml           # Docker compose orchestration
├── cloudbuild.yaml              # Google Cloud Build configuration
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **API Key**: Groq API key (free tier available at [console.groq.com](https://console.groq.com))
- **Ollama** (optional, for local LLM inference)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/AustraliaJobSeeker-AI.git
   cd AustraliaJobSeeker-AI
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   BACKEND_URL=http://127.0.0.1:8000
   API_TIMEOUT=120
   MAX_RETRIES=2
   ```

5. **Run the backend server**
   ```bash
   # Start A2A server (port 9999)
   python -m A2A.main

   # In another terminal, start FastAPI backend (port 8000)
   python -m api.main
   ```

6. **Run the frontend**
   ```bash
   streamlit run frontend/app.py
   ```

   The application will open at `http://localhost:8501`

## 🔧 Component Overview

### Frontend (Streamlit)
- **Location**: `frontend/app.py`
- **Port**: 8501
- **Features**:
  - Resume upload and editing
  - Job search form with location and visa filters
  - Real-time job ranking
  - Resume and cover letter generation with download
  - Health status monitoring

### Backend API (FastAPI)
- **Location**: `api/main.py`
- **Port**: 8000
- **Endpoints**:
  - `POST /search-jobs` - Search for jobs with filters
  - `POST /generate-resume` - Generate tailored resume
  - `POST /generate-cover-letter` - Generate cover letter
  - `GET /health` - Health check

### A2A Server
- **Location**: `A2A/main.py`
- **Port**: 9999
- **Purpose**: Exposes agent capabilities via A2A Protocol for tool use
- **Features**: Agent skill discovery and execution

### Agents (LangGraph)
- **Supervisor Agent**: Orchestrates multi-agent workflow
- **Router Agent**: Routes queries to appropriate specialized agents
- **Job Enrichment Agent**: Analyzes and enriches job descriptions
- **Ranking Agent**: Scores and ranks jobs by profile fit
- **Resume Agent**: Generates tailored resumes
- **Cover Letter Agent**: Generates personalized cover letters
- **Profile Agent**: Manages user profiles and preferences
- **Visa Agent**: Checks visa eligibility

### Tools
- **Job Scraper**: Extracts job listings from Seek.com.au
- **Job Details Scraper**: Retrieves detailed job information
- **Resume/Cover Letter Tools**: Text processing and generation

## 🐳 Docker Deployment

### Single Container (Docker Compose)

```bash
cd Docker
docker-compose up --build
```

Access:
- Frontend: http://localhost:8501
- Backend: http://localhost:8000
- A2A Server: http://localhost:9999

### Manual Docker Build

```bash
# Build the image
docker build -t australiajobseeker-ai:latest .

# Run container
docker run -p 8501:8501 -p 8000:8000 -p 9999:9999 \
  -e GROQ_API_KEY=your_key \
  -e BACKEND_URL=http://app:8000 \
  australiajobseeker-ai:latest
```

## ☸️ Kubernetes Deployment

See [kubernetes/README.md](kubernetes/README.md) for comprehensive Kubernetes deployment guide including:
- Prerequisites and setup
- Architecture overview
- Step-by-step deployment
- Configuration management
- Monitoring and scaling

Quick deploy:
```bash
cd kubernetes
kubectl apply -f .
```

## ☁️ Google Cloud Run Deployment

See [CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md) for detailed Google Cloud Run setup.

```bash
gcloud run deploy australiajobseeker-ai \
  --source . \
  --region us-central1 \
  --set-env-vars GROQ_API_KEY=your_key
```

## 🧪 Testing

Run tests to verify functionality:

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_job_enrichment.py -v

# Run with coverage
pytest tests/ --cov=agents --cov=tools
```

Key test files:
- `tests/test_langgraph_supervisor.py` - Multi-agent orchestration
- `tests/test_job_enrichment.py` - Job analysis
- `tests/test_ranking_agent.py` - Job ranking
- `tests/test_resume_agent.py` - Resume generation
- `tests/test_cover_letter_agent.py` - Cover letter generation

## 📊 Monitoring & Logging

### LangSmith Integration

```python
# Enable LangSmith tracing
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=your_langsmith_key
export LANGCHAIN_PROJECT="australiajobseeker-ai"
```

### Frontend Logging
- Structured logging with timestamps
- Environment configurable via `LOG_LEVEL`
- Detailed error messages and debug info

### Backend Logging
- FastAPI request/response logging
- Agent execution traces
- Tool invocation logs

## 🔐 Security Considerations

- **API Keys**: Store all API keys in `.env` (never commit to git)
- **Input Validation**: All user inputs validated before processing
- **CORS**: Configure CORS appropriately for production
- **Rate Limiting**: Implement rate limiting on API endpoints
- **Data Privacy**: Resume and cover letter data processed locally

## 📚 Documentation Files

- [FRONTEND_PRODUCTION_GUIDE.md](FRONTEND_PRODUCTION_GUIDE.md) - Production frontend features and configuration
- [kubernetes/README.md](kubernetes/README.md) - Kubernetes deployment guide
- [CLOUD_RUN_DEPLOYMENT.md](CLOUD_RUN_DEPLOYMENT.md) - Google Cloud Run setup
- [A2A/README.md](A2A/README.md) - A2A protocol and agent capabilities
- [MCP/MCP_client/README.md](MCP/MCP_client/README.md) - Model Context Protocol integration

## 🛠️ Technology Stack

- **LLM Framework**: LangChain, LangGraph
- **LLM Provider**: Groq API (free tier)
- **Frontend**: Streamlit
- **Backend**: FastAPI, Uvicorn
- **Web Scraping**: Playwright, BeautifulSoup4
- **Data Validation**: Pydantic
- **Agent Protocol**: A2A SDK
- **Containerization**: Docker, Kubernetes
- **Cloud Deployment**: Google Cloud Run
- **Monitoring**: LangSmith

## 📋 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | Required | Groq API key for LLM |
| `BACKEND_URL` | http://127.0.0.1:8000 | Backend API base URL |
| `API_TIMEOUT` | 120 | API request timeout in seconds |
| `MAX_RETRIES` | 2 | Maximum retry attempts for API calls |
| `RETRY_DELAY` | 1.0 | Initial retry delay in seconds |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LANGCHAIN_TRACING_V2` | false | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | Optional | LangSmith API key |
| `LANGCHAIN_PROJECT` | Optional | LangSmith project name |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Backend not responding
- Check if FastAPI is running on port 8000
- Verify `BACKEND_URL` environment variable
- Check backend logs for errors

### Resume/Cover letter generation fails
- Verify Groq API key is valid
- Check API rate limits
- Ensure resume text is valid (10+ words)

### Job scraping returns no results
- Verify internet connection
- Check if Seek.com.au is accessible
- Review scraper for any website changes

### Kubernetes deployment issues
- Check pod status: `kubectl get pods -n australiajobseeker`
- Review logs: `kubectl logs -n australiajobseeker <pod-name>`
- Verify resource limits and requests

## 📞 Support

For issues and questions:
1. Check existing issues on GitHub
2. Review documentation files
3. Create a new issue with detailed information

## 🙏 Acknowledgments

- LangChain and LangGraph communities
- Groq for free LLM API tier
- Streamlit for excellent frontend framework
- Kubernetes community

---

**Built with ❤️ for job seekers in Australia**
