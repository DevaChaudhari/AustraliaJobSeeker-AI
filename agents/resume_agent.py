from langchain_ollama import ChatOllama
import os

# Ollama host configurable for Docker/K8s deployment
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

llm = ChatOllama(
    model="llama3:8b",
    temperature=0,
    base_url=OLLAMA_HOST
)


def tailor_resume(
    resume_text: str,
    job_description: str
):

    prompt = f"""
You are an Australian resume expert.

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

    try:
        response = llm.invoke(
            prompt
        )
        tailored_resume = response.content
    except Exception as e:
        return f"LLM error: {e}"

    with open(
        "data/generated_resume.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(tailored_resume)

    return tailored_resume