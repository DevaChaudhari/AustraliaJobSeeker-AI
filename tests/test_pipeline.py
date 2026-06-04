from tools.seek_scraper import search_seek
from agents.job_enrichment_agent import enrich_job
from agents.visa_agent import check_visa_eligibility


jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

job = jobs[0]

enriched_job = enrich_job(job)

result = check_visa_eligibility(
    enriched_job["full_description"],
    "500"
)

print("\nTITLE:")
print(job["title"])

print("\nCOMPANY:")
print(job["company"])

print("\nVISA RESULT:")
print(result)