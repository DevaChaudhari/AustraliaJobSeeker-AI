from langchain_groq import ChatGroq
import os

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0.3,
)


def generate_cover_letter(
    resume_text: str,
    job_description: str,
    company: str,
    title: str
):

    prompt = f"""
You are an Australian career coach.

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

    try:
        response = llm.invoke(prompt)
        cover_letter = response.content
    except Exception as e:
        return f"LLM error: {e}"

    file_path = os.path.abspath(
        "data/generated_cover_letter.txt"
    )

    print("\nSaving cover letter to:")
    print(file_path)

    with open("/tmp/generated_cover_letter.txt", "w", encoding="utf-8") as f:
        f.write(cover_letter)

    return cover_letter