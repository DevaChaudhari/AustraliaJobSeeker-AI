from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3:8b",
    temperature=0
)


def route_query(
    user_query: str
):

    prompt = f"""
You are a supervisor agent.

Available agents:

1. search_agent
   - Finds jobs

2. visa_agent
   - Checks visa eligibility

3. ranking_agent
   - Ranks jobs

4. resume_agent
   - Tailors resumes

Return ONLY ONE agent name.

User Query:
{user_query}
"""

    response = llm.invoke(
        prompt
    )

    return (
        response.content
        .strip()
        .lower()
    )