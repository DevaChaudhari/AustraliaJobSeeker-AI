from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
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

    response = llm.invoke(prompt)

    return (
        response.content
        .strip()
        .lower()
    )