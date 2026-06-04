import re


COMMON_SKILLS = [
    "python",
    "sql",
    "machine learning",
    "deep learning",
    "langchain",
    "langgraph",
    "docker",
    "aws",
    "azure",
    "gcp",
    "tensorflow",
    "pytorch",
    "llm",
    "ai",
    "automation",
    "data engineering",
    "data analysis",
    "power bi",
    "tableau",
    "git",
    "fastapi",
    "streamlit"
]


def extract_skills(text: str):

    text = text.lower()

    found_skills = []

    for skill in COMMON_SKILLS:

        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))


def calculate_match_score(
    resume_text: str,
    job_description: str
):

    resume_skills = extract_skills(
        resume_text
    )

    job_skills = extract_skills(
        job_description
    )

    matched_skills = list(
        set(resume_skills)
        &
        set(job_skills)
    )

    missing_skills = list(
        set(job_skills)
        -
        set(resume_skills)
    )

    if len(job_skills) == 0:

        score = 0

    else:

        score = int(
            (
                len(matched_skills)
                /
                len(job_skills)
            ) * 100
        )

    return {
        "match_score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }