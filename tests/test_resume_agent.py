from tools.seek_scraper import search_seek
from agents.job_enrichment_agent import enrich_job
from agents.resume_agent import tailor_resume


jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

job = enrich_job(jobs[0])

with open(
    "data/sample_resume.txt",
    "r",
    encoding="utf-8"
) as f:

    resume_text = f.read()

tailored_resume = tailor_resume(
    resume_text=resume_text,
    job_description=job["full_description"]
)

print(tailored_resume)