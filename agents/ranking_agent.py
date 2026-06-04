from agents.profile_agent import (
    calculate_match_score
)


def calculate_job_score(
    job,
    resume_text
):

    score = 0
    has_resume = bool(resume_text and resume_text.strip())

    visa_result = job.get(
        "visa_result",
        {}
    )

    if visa_result.get(
        "eligible",
        False
    ):
        score += 100

    if has_resume:

        profile_result = (
            calculate_match_score(
                resume_text,
                job["full_description"]
            )
        )

        score += (
            profile_result[
                "match_score"
            ]
        )

    else:

        profile_result = {
            "match_score": None,
            "matched_skills": [],
            "missing_skills": [],
            "message": "Upload a resume to calculate match score."
        }

    job["profile_result"] = (
        profile_result
    )

    description = (
        job["full_description"]
        .lower()
    )

    keywords = [
        "ai",
        "machine learning",
        "llm",
        "artificial intelligence",
        "automation",
        "python"
    ]

    relevance = 0

    for keyword in keywords:

        if keyword in description:
            relevance += 10

    score += relevance

    return score


def remove_duplicates(jobs):

    seen = set()

    unique_jobs = []

    for job in jobs:

        key = (
            job["title"].lower(),
            job["company"].lower()
        )

        if key not in seen:

            seen.add(key)

            unique_jobs.append(job)

    return unique_jobs


def rank_jobs(
    jobs,
    resume_text=None
):

    jobs = remove_duplicates(
        jobs
    )

    for job in jobs:

        job["job_score"] = (
            calculate_job_score(
                job,
                resume_text
            )
        )

    jobs.sort(
        key=lambda x:
        x["job_score"],
        reverse=True
    )

    return jobs
