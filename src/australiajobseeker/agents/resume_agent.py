from langchain_groq import ChatGroq
import os

# Groq retires models periodically; override with the GROQ_MODEL environment variable.
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def _get_llm(temperature=0):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Set it in your environment or .env file."
        )
    return ChatGroq(model=GROQ_MODEL, temperature=temperature, api_key=api_key)


def tailor_resume(resume_text: str, job_description: str) -> str:
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
    llm = _get_llm(temperature=0)
    # gpt-oss models occasionally return empty content; retry, then fail loudly.
    for _ in range(3):
        response = llm.invoke(prompt)
        if response.content and response.content.strip():
            break
    else:
        raise RuntimeError("The model returned an empty response. Please try again.")
    tailored_resume = response.content

    try:
        with open("/tmp/generated_resume.txt", "w", encoding="utf-8") as f:
            f.write(tailored_resume)
    except Exception:
        pass

    return tailored_resume
