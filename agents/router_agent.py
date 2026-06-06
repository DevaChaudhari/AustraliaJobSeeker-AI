from langchain_groq import ChatGroq
import os

GROQ_MODEL = "llama-3.1-8b-instant"


def _get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")
    return ChatGroq(model=GROQ_MODEL, temperature=0, api_key=api_key)


def route_query(user_query: str):
    prompt = f"""You are a supervisor agent.

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
    llm = _get_llm()
    response = llm.invoke(prompt)
    return response.content.strip().lower()
