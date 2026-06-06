from langchain_groq import ChatGroq
import os

GROQ_MODEL = "llama-3.1-8b-instant"


def _get_llm(temperature=0.3):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Add it in Cloud Run → Edit & Deploy New Revision → Variables & Secrets."
        )
    return ChatGroq(model=GROQ_MODEL, temperature=temperature, api_key=api_key)


def generate_cover_letter(
    resume_text: str,
    job_description: str,
    company: str,
    title: str
) -> str:
    prompt = f"""You are an Australian career coach.

Write a professional Australian-style cover letter.

Candidate Resume:
{resume_text}

Job Title:
{title}

Company:
{company}

Job Description:
{job_description}

Requirements:
- Australian professional style
- 300-500 words
- Mention relevant skills
- Match the job requirements
- Sound natural
- Do not invent experience
- End professionally

Return only the cover letter.
"""
    llm = _get_llm(temperature=0.3)
    response = llm.invoke(prompt)
    cover_letter = response.content

    try:
        with open("/tmp/generated_cover_letter.txt", "w", encoding="utf-8") as f:
            f.write(cover_letter)
    except Exception:
        pass

    return cover_letter
