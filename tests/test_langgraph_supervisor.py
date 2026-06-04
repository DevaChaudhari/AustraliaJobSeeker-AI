from agents.langgraph_supervisor import (
    graph
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
        "resume_text": resume_text,
        "jobs": []
    }
)

print()

print(
    "TOTAL JOBS:"
)

print(
    len(result["jobs"])
)

print()

top_job = result["jobs"][0]

print(
    "TOP JOB:"
)

print()

print(
    top_job["title"]
)

print()

print(
    "SCORE:",
    top_job["job_score"]
)

print()

print(
    "ELIGIBLE:",
    top_job["visa_result"]["eligible"]
)