import asyncio
import json
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

load_dotenv()

SERVERS = {
    "devendra": {
        "transport": "streamable_http",
        "url": "https://devendra.fastmcp.app/mcp",
        "headers": {"Authorization": f"Bearer {os.getenv('MCP_API_KEY')}"}
    }
}

async def main():
    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}
    print("Available tools:", list(named_tools.keys()))

    llm = ChatGroq(
        model="llama3-8b-8192",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content="You are a helpful Australian job search assistant. Use the available tools to help users find jobs, generate cover letters, and check visa eligibility."),
        HumanMessage(content="Search for software engineer jobs in Adelaide")
    ]

    response = await llm_with_tools.ainvoke(messages)

    if not getattr(response, "tool_calls", None):
        print("\nLLM Reply:", response.content)
        return

    messages.append(response)

    for tc in response.tool_calls:
        tool_name = tc["name"]
        tool_args = tc.get("args") or {}
        tool_id = tc["id"]

        print(f"\nCalling tool: {tool_name}")
        print(f"With args: {tool_args}")

        result = await named_tools[tool_name].ainvoke(tool_args)
        messages.append(ToolMessage(
            tool_call_id=tool_id,
            content=json.dumps(result)
        ))

    final = await llm.ainvoke(messages)
    print(f"\nFinal response: {final.content}")

if __name__ == '__main__':
    asyncio.run(main())