# A2A Server

Exposes the job-seeker capabilities to other agents through the [A2A protocol](https://a2a-protocol.org). Source: [`src/australiajobseeker/a2a_server/`](../src/australiajobseeker/a2a_server).

## Run

```bash
uv run python -m australiajobseeker.a2a_server.main   # listens on :9999
```

The agent card is served at `http://localhost:9999/.well-known/agent-card.json`.

## Skills

| Skill ID | Description |
|----------|-------------|
| `generate_cover_letter` | Tailored cover letter from a resume and job description |
| `generate_tailored_resume` | Rewrite a resume for a job description |
| `search_jobs` | Search SEEK for a role and location |
| `scrape_job_description` | Full description for one job URL |
| `scrape_multiple_job_descriptions` | Full descriptions for several job URLs |
| `check_visa_eligibility` | Check a job ad against a visa type (500, 485, 482, PR) |

## Layout

| File | Purpose |
|------|---------|
| `main.py` | Declares the agent card and skills, starts the Starlette app |
| `agent_executor.py` | Dispatches an incoming skill request to the matching agent or scraper |
| `client.py` | Example A2A client: `uv run python -m australiajobseeker.a2a_server.client` |
