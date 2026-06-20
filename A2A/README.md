# A2A Server - Agent Capability Exposure

The A2A (Agentive-to-Agentive) Server exposes specialized agents and their capabilities through the A2A protocol, enabling external systems to discover and invoke agent functions.

## 📋 Overview

The A2A Server acts as a bridge between the multi-agent system and external applications. It provides:

- **Agent Discovery**: List all available agents and their capabilities
- **Skill Exposure**: Expose specialized functions as callable agent skills
- **Unified Interface**: Single entry point for agent access (Port 9999)
- **Agent Orchestration**: Route requests to appropriate specialized agents

### Agent Skills

| Skill ID | Name | Description | Tags |
|----------|------|-------------|------|
| `generate_cover_letter` | Generate Cover Letter | Generate tailored cover letter from resume & job description | cover letter, resume, writing |
| `scrape_job_description` | Scrape Job Description | Fetch full job description from a single URL | scraping, job, url |
| `scrape_multiple_job_descriptions` | Scrape Multiple Jobs | Scrape job descriptions from multiple URLs | scraping, bulk, jobs |
| `generate_tailored_resume` | Generate Tailored Resume | Tailor resume to match specific job description | resume, tailoring, writing |
| `rank_jobs` | Rank Jobs | Score and rank jobs by profile fit | ranking, scoring, analysis |
| `search_jobs` | Search Jobs | Search for visa-friendly AI jobs in Australia | search, jobs, visa |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Groq API key
- Ollama (optional, for local LLM)

### Running the Server

```bash
# From project root
python -m A2A.main
```

Server runs on port **9999** by default.

### Environment Variables

```bash
export GROQ_API_KEY=your_groq_api_key_here
export OLLAMA_HOST=http://localhost:11434  # Optional
export A2A_PORT=9999                       # Optional
export LOG_LEVEL=INFO                      # Optional
```

## 🔌 API Endpoints

### List Available Agents

```bash
GET http://localhost:9999/agents
```

**Response:**
```json
{
  "agents": [
    {
      "id": "job_enrichment_agent",
      "name": "Job Enrichment Agent",
      "description": "Analyzes and enriches job descriptions with structured insights",
      "capabilities": [...]
    }
  ]
}
```

### List Agent Skills

```bash
GET http://localhost:9999/agents/{agent_id}/skills
```

**Response:**
```json
{
  "agent_id": "cover_letter_agent",
  "skills": [
    {
      "id": "generate_cover_letter",
      "name": "Generate Cover Letter",
      "description": "Generate a tailored cover letter based on a resume and job description",
      "tags": ["cover letter", "resume", "job application", "writing"],
      "examples": [
        "Generate a cover letter for a Software Engineer role at Google",
        "Write a cover letter using my resume for this job description"
      ]
    }
  ]
}
```

### Invoke Agent

```bash
POST http://localhost:9999/invoke
Content-Type: application/json

{
  "agent_id": "cover_letter_agent",
  "input": {
    "resume": "Your resume text here...",
    "job_description": "Job description text here..."
  }
}
```

**Response:**
```json
{
  "status": "success",
  "output": "Generated cover letter text...",
  "metadata": {
    "agent_id": "cover_letter_agent",
    "execution_time": 2.45
  }
}
```

## 📁 File Structure

```
A2A/
├── main.py              # Entry point - starts A2A server
├── agent_executor.py    # Executes agents and handles A2A protocol
├── client.py            # A2A client for invoking agents
└── README.md            # This file
```

### main.py

Initializes and starts the A2A server. Exposes agent capabilities through:

```python
from A2A.main import main

if __name__ == "__main__":
    main()  # Starts server on port 9999
```

**Agent Skills Definition:**
- Cover Letter Generation
- Job Description Scraping (single & multiple)
- Resume Tailoring
- Job Ranking
- Job Search
- And more...

### agent_executor.py

Handles agent execution logic:

```python
from A2A.agent_executor import AgentExecutor

executor = AgentExecutor()
result = await executor.execute(agent_id, input_data)
```

### client.py

Python client for invoking A2A agents:

```python
from A2A.client import A2AClient

client = A2AClient("http://localhost:9999")
agents = await client.list_agents()
result = await client.invoke_agent("cover_letter_agent", {...})
```

## 🔄 Integration Examples

### With FastAPI Backend

```python
from A2A.client import A2AClient
from fastapi import FastAPI

app = FastAPI()
a2a_client = A2AClient("http://localhost:9999")

@app.post("/generate-cover-letter")
async def generate_cover_letter(resume: str, job_description: str):
    result = await a2a_client.invoke_agent(
        "cover_letter_agent",
        {"resume": resume, "job_description": job_description}
    )
    return result
```

### With Streamlit Frontend

```python
import requests

def call_a2a_agent(agent_id, input_data):
    response = requests.post(
        "http://localhost:9999/invoke",
        json={"agent_id": agent_id, "input": input_data}
    )
    return response.json()

# Usage
cover_letter = call_a2a_agent(
    "cover_letter_agent",
    {"resume": resume_text, "job_description": job_desc}
)
```

### Direct Agent Invocation

```python
from agents.cover_letter_agent import CoverLetterAgent

agent = CoverLetterAgent()
result = agent.invoke({
    "resume": resume_text,
    "job_description": job_description
})
print(result["output"])
```

## 🧪 Testing

```bash
# Test A2A server connectivity
curl http://localhost:9999/agents

# Test agent skill invocation
curl -X POST http://localhost:9999/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "cover_letter_agent",
    "input": {
      "resume": "Sample resume",
      "job_description": "Sample job description"
    }
  }'

# Run A2A tests
pytest tests/ -k "a2a" -v
```

## 🔐 Security

- **API Authentication**: Consider adding API key authentication in production
- **Rate Limiting**: Implement rate limiting to prevent abuse
- **Input Validation**: All inputs validated before agent execution
- **Error Handling**: Secure error messages (no sensitive data exposure)

### Production Recommendations

```python
# Add authentication middleware
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.post("/invoke")
async def invoke(api_key: str = Depends(api_key_header)):
    # Verify API key
    verify_api_key(api_key)
    # Process request...
```

## 📊 Monitoring & Logging

### Structured Logging

```python
import logging

logger = logging.getLogger("A2A")
logger.info(f"Agent invoked: {agent_id}")
logger.error(f"Agent execution failed: {error}")
```

### Execution Metrics

Track in monitoring system:
- Agent invocation count by skill
- Execution time distribution
- Error rates and types
- Success/failure ratios

Example with LangSmith:

```python
from langsmith import traceable

@traceable(name="invoke_agent")
async def invoke_agent(agent_id: str, input_data: dict):
    # Agent execution logic
    ...
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 9999

CMD ["python", "-m", "A2A.main"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: a2a-server
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: a2a
        image: australiajobseeker-ai:latest
        ports:
        - containerPort: 9999
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: groq-secret
              key: api-key
```

## 🔗 Related Documentation

- [Main README](../README.md) - Project overview
- [FastAPI Backend](../api/main.py) - REST API endpoints
- [Agents](../agents/) - Individual agent implementations
- [Frontend](../frontend/app.py) - Streamlit application

## ❓ FAQ

**Q: What's the difference between A2A and FastAPI backends?**
A: FastAPI exposes REST endpoints, A2A exposes agent capabilities via A2A protocol.

**Q: Can I run both A2A and FastAPI simultaneously?**
A: Yes! They run on different ports (9999 and 8000) and can coexist.

**Q: How do I add a new agent skill?**
A: Define the skill in the agent's `main.py` and add it to the A2A agent card.

**Q: Is authentication required?**
A: Not by default, but recommended for production deployments.

**Q: What's the maximum request size?**
A: Configure in FastAPI settings; default is reasonable for job descriptions.

## 🛟 Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 9999 already in use | `export A2A_PORT=9998` or kill process using port |
| Agent returns empty result | Check Groq API key and rate limits |
| Slow responses | Monitor LLM inference time; consider caching |
| Connection refused | Ensure A2A server is running on correct port |

---

**A2A Protocol integration for AustraliaJobSeeker AI**
