from agents.supervisor_graph import graph
from agents.ranking_agent import (
    rank_jobs
)

with open(
    "data/sample_resume.txt",
    "r",
    encoding="utf-8"
) as f:

    resume_text = f.read()

result = graph.invoke(
    {
        "role": "AI Engineer",
        "location": "All Adelaide SA",
        "visa_type": "500",
        "jobs": []
    }
)

ranked_jobs = rank_jobs(
    result["jobs"],
    resume_text
)

print("\nTOP JOBS\n")

for job in ranked_jobs[:5]:

    print("=" * 60)

    print(
        f"TITLE: {job['title']}"
    )

    print(
        f"SCORE: {job['job_score']}"
    )

    print(
        f"MATCH SCORE: "
        f"{job['profile_result']['match_score']}"
    )

    print(
        f"ELIGIBLE: "
        f"{job['visa_result']['eligible']}"
    )

    print(
        f"MISSING SKILLS: "
        f"{job['profile_result']['missing_skills']}"
    )

    print()