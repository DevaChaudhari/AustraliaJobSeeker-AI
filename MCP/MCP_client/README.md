# MCP Client - Model Context Protocol Integration

The MCP (Model Context Protocol) Client provides integration with MCP servers, enabling AI agents to access external tools and data sources through the standardized Model Context Protocol.

## 📋 Overview

The MCP Client connects LangChain agents to MCP servers, exposing:

- **Tool Discovery**: Browse available tools from MCP servers
- **Resource Access**: Access remote resources and data
- **Unified Interface**: Seamless integration with LangChain workflows
- **Error Handling**: Robust error recovery and retry logic

### Capabilities

- ✅ Connect to multiple MCP servers
- ✅ Discover and list available tools
- ✅ Execute tool calls with parameter validation
- ✅ Stream responses for long-running operations
- ✅ Handle authentication and credentials
- ✅ Resource management and cleanup

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MCP Server running (local or remote)
- LangChain installed

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from MCP.MCP_client.main import MCPClient

# Initialize client
client = MCPClient(server_url="http://localhost:3001")

# List available tools
tools = await client.list_tools()
for tool in tools:
    print(f"- {tool.name}: {tool.description}")

# Execute a tool
result = await client.call_tool(
    tool_name="read_file",
    arguments={"path": "/etc/hostname"}
)
print(result)

# List available resources
resources = await client.list_resources()
for resource in resources:
    print(f"📄 {resource.name}: {resource.uri}")

# Access a resource
content = await client.read_resource(uri="file:///path/to/data.json")
```

## 📁 File Structure

```
MCP/MCP_client/
├── main.py              # MCP client implementation
├── pyproject.toml       # Project configuration
├── README.md            # This file
└── requirements.txt     # Dependencies
```

### main.py

Core MCP client implementation:

```python
from MCP.MCP_client.main import MCPClient

class MCPClient:
    """Connect to and interact with MCP servers."""
    
    async def __init__(self, server_url: str):
        """Initialize connection to MCP server."""
        
    async def list_tools(self) -> List[Tool]:
        """List all available tools from server."""
        
    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute a tool on the MCP server."""
        
    async def list_resources(self) -> List[Resource]:
        """List all available resources from server."""
        
    async def read_resource(self, uri: str) -> str:
        """Read content from a resource."""
        
    async def close(self):
        """Close connection to MCP server."""
```

## 🔌 Integration with LangChain Agents

### Connect MCP Tools to LangChain

```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from MCP.MCP_client.main import MCPClient

# Initialize MCP client
mcp_client = MCPClient("http://localhost:3001")

# Get tools from MCP server
mcp_tools = await mcp_client.list_tools()

# Convert MCP tools to LangChain tools
langchain_tools = []
for mcp_tool in mcp_tools:
    tool = Tool(
        name=mcp_tool.name,
        func=lambda **kwargs, t=mcp_tool: await mcp_client.call_tool(t.name, kwargs),
        description=mcp_tool.description
    )
    langchain_tools.append(tool)

# Create agent with MCP tools
llm = ChatOpenAI(model="gpt-4")
agent = initialize_agent(
    langchain_tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
result = await agent.arun("Execute task using MCP tools")
```

### Custom Tool Wrapper

```python
from langchain.tools import StructuredTool

async def call_mcp_tool(tool_name: str, **kwargs):
    """Wrapper for MCP tool calls."""
    mcp_client = MCPClient("http://localhost:3001")
    return await mcp_client.call_tool(tool_name, kwargs)

# Create structured tool
mcp_tool = StructuredTool(
    name="mcp_executor",
    func=call_mcp_tool,
    description="Execute commands via MCP server",
    args_schema=MCPToolInput
)
```

## 📋 Configuration

### pyproject.toml

```toml
[project]
name = "mcp-client"
version = "0.1.0"
description = "MCP Client for AustraliaJobSeeker AI"
requires-python = ">=3.10"
dependencies = [
    "langchain>=1.3.2",
    "langchain-community>=0.1.0",
    "fastmcp>=0.1.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
]
```

### Environment Variables

```bash
# MCP Server configuration
MCP_SERVER_URL=http://localhost:3001
MCP_SERVER_TIMEOUT=30
MCP_SERVER_RETRIES=3

# Optional authentication
MCP_API_KEY=your_api_key_here
MCP_API_SECRET=your_api_secret_here

# Logging
MCP_LOG_LEVEL=INFO
```

## 🔄 Common Use Cases

### 1. File Access Tool

```python
# List files in a directory
files = await client.call_tool(
    "list_files",
    {"path": "/home/user/data"}
)

# Read file content
content = await client.call_tool(
    "read_file",
    {"path": "/home/user/data/input.txt"}
)

# Write file
await client.call_tool(
    "write_file",
    {"path": "/home/user/data/output.txt", "content": "data"}
)
```

### 2. Web Search Integration

```python
# Search web
results = await client.call_tool(
    "web_search",
    {"query": "Python best practices"}
)

# Fetch URL content
html = await client.call_tool(
    "fetch_url",
    {"url": "https://example.com"}
)
```

### 3. Database Query

```python
# Execute SQL query
results = await client.call_tool(
    "query_database",
    {
        "database": "postgres",
        "query": "SELECT * FROM jobs WHERE location = 'Sydney'"
    }
)
```

### 4. API Integration

```python
# Call external API
data = await client.call_tool(
    "http_request",
    {
        "method": "GET",
        "url": "https://api.example.com/data",
        "headers": {"Authorization": "Bearer token"}
    }
)
```

## 🧪 Testing

### Run Tests

```bash
pytest tests/
```

### Example Test

```python
import pytest
from MCP.MCP_client.main import MCPClient

@pytest.fixture
async def mcp_client():
    """Create MCP client for testing."""
    client = MCPClient("http://localhost:3001")
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_list_tools(mcp_client):
    """Test tool discovery."""
    tools = await mcp_client.list_tools()
    assert len(tools) > 0
    assert any(t.name == "read_file" for t in tools)

@pytest.mark.asyncio
async def test_call_tool(mcp_client):
    """Test tool execution."""
    result = await mcp_client.call_tool(
        "echo",
        {"message": "hello"}
    )
    assert result == "hello"
```

### Mock Testing

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_mcp_with_mock():
    """Test with mocked MCP server."""
    with patch('MCP.MCP_client.main.httpx.AsyncClient') as mock_client:
        mock_client.return_value.get.return_value.json.return_value = {
            "tools": [{"name": "test", "description": "Test tool"}]
        }
        client = MCPClient("http://localhost:3001")
        tools = await client.list_tools()
        assert len(tools) == 1
```

## 🚀 Deployment

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

ENV MCP_SERVER_URL=http://mcp-server:3001

CMD ["python", "-m", "MCP.MCP_client.main"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-client
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: mcp-client
        image: australiajobseeker-ai:latest
        env:
        - name: MCP_SERVER_URL
          value: "http://mcp-server:3001"
        - name: MCP_SERVER_TIMEOUT
          value: "30"
```

## 🔐 Security

### Authentication

```python
# Basic auth
client = MCPClient(
    server_url="http://localhost:3001",
    auth_type="basic",
    username="user",
    password="password"
)

# API key auth
client = MCPClient(
    server_url="http://localhost:3001",
    auth_type="apikey",
    api_key="your_api_key"
)

# Bearer token
client = MCPClient(
    server_url="http://localhost:3001",
    auth_type="bearer",
    token="your_token"
)
```

### Error Handling

```python
from MCP.MCP_client.main import MCPClient, MCPError, TimeoutError

try:
    result = await client.call_tool("risky_tool", {})
except TimeoutError:
    print("MCP server request timed out")
except MCPError as e:
    print(f"MCP error: {e.message}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    await client.close()
```

## 📊 Monitoring

### Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("MCP_CLIENT")

client = MCPClient(
    server_url="http://localhost:3001",
    logger=logger
)
```

### Metrics

Track with monitoring system:
- Tool execution count
- Execution time per tool
- Error rates by tool
- Server availability

## 🔗 Related Documentation

- [MCP Server README](../MCP_servers/README.md)
- [Main Project README](../../README.md)
- [LangChain Integration](../../agents/)
- [A2A Server](../../A2A/README.md)

## ❓ FAQ

**Q: What's Model Context Protocol (MCP)?**
A: MCP is a standardized protocol for AI models to interact with external tools, APIs, and data sources.

**Q: Can I connect to multiple MCP servers?**
A: Yes, create separate client instances for each server.

**Q: How do I handle long-running operations?**
A: Use streaming responses or webhook callbacks for notifications.

**Q: What's the authentication overhead?**
A: Minimal; credentials cached after initial authentication.

**Q: Can MCP clients run offline?**
A: No, they require connection to MCP server.

## 🛟 Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Verify MCP server is running and URL is correct |
| Tool not found | Check `list_tools()` output; verify tool name |
| Timeout errors | Increase `MCP_SERVER_TIMEOUT` environment variable |
| Auth failures | Verify credentials and authentication method |
| High latency | Check network connectivity and server load |

## 📞 Support

For issues:
1. Check MCP server logs
2. Enable DEBUG logging
3. Verify network connectivity
4. Review MCP specification

---

**MCP Client for AustraliaJobSeeker AI**
