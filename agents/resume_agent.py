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
        temperature=0,
        api_key=api_key
    )


def tailor_resume(
    resume_text: str,
    job_description: str
) -> str:

    prompt = f"""You are an Australian resume expert.

TASK:
Rewrite and improve the resume so it better matches the job description.

RULES:
- Keep information truthful
- Use Australian resume style
- Highlight relevant skills
- Improve wording
- Keep professional formatting

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}
"""

    llm = _get_llm()
    response = llm.invoke(prompt)
    tailored_resume = response.content

    # Use /tmp — the only writable directory in Cloud Run
    try:
        with open("/tmp/generated_resume.txt", "w", encoding="utf-8") as f:
            f.write(tailored_resume)
    except Exception:
        pass  # saving is optional; don't crash if it fails

    return tailored_resume