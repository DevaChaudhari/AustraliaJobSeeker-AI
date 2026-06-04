from tools.seek_scraper import search_seek
from agents.visa_agent import check_visa_eligibility


jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

job = jobs[0]

result = check_visa_eligibility(
    job_description=job["description"],
    visa_type="500"
)

print("\nJOB:")
print(job["title"])

print("\nRESULT:")
print(result)