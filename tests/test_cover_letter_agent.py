from agents.supervisor_graph import graph

from agents.cover_letter_agent import (
    generate_cover_letter
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

job = result["jobs"][0]

cover_letter = generate_cover_letter(
    resume_text=resume_text,
    job_description=job["full_description"],
    company=job["company"],
    title=job["title"]
)

print("\nCOVER LETTER\n")

print(cover_letter)