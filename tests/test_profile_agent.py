from tools.seek_scraper import search_seek
from agents.job_enrichment_agent import enrich_job
from agents.profile_agent import (
    calculate_match_score
)

with open(
    "data/sample_resume.txt",
    "r",
    encoding="utf-8"
) as f:

    resume_text = f.read()

jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

job = enrich_job(
    jobs[0]
)

result = calculate_match_score(
    resume_text,
    job["full_description"]
)

print("\nMATCH RESULT\n")

print(result)