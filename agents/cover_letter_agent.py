from langchain_groq import ChatGroq
import os


def _get_llm():
    """Create LLM instance at call time so env vars are always fresh."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Add it in Cloud Run → Edit & Deploy New Revision → Variables & Secrets."
        )
    return ChatGroq(
        model="llama3-8b-8192",
        temperature=0.3,
        api_key=api_key
    )


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

    llm = _get_llm()
    response = llm.invoke(prompt)
    cover_letter = response.content

    # Use /tmp — the only writable directory in Cloud Run
    try:
        with open("/tmp/generated_cover_letter.txt", "w", encoding="utf-8") as f:
            f.write(cover_letter)
        print("Cover letter saved to /tmp/generated_cover_letter.txt")
    except Exception:
        pass  # saving is optional; don't crash if it fails

    return cover_letter