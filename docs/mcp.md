# MCP

## Server

[`src/australiajobseeker/mcp_server/server.py`](../src/australiajobseeker/mcp_server/server.py) exposes the same capabilities as [FastMCP](https://gofastmcp.com) tools. The FastMCP object is `mcp`:

```bash
uv run fastmcp run src/australiajobseeker/mcp_server/server.py:mcp
```

Tools: `generate_job_cover_letter`, `generate_tailored_resume`, `search_jobs`, `scrape_job_description`, `scrape_multiple_job_descriptions`, `check_job_visa_eligibility`.

## Example client

[`examples/mcp_client.py`](../examples/mcp_client.py) connects to a deployed MCP server with `langchain-mcp-adapters`, lets a Groq model pick tools, and prints the result. It needs `MCP_API_KEY` and `GROQ_API_KEY` in `.env`, and the server URL in the script pointed at your deployment.

```bash
uv run python examples/mcp_client.py
```
