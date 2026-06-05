from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
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
        response = llm.invoke(prompt)
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