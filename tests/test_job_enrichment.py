from tools.seek_scraper import search_seek
from agents.job_enrichment_agent import (
    enrich_job
)


jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

job = jobs[0]

enriched_job = enrich_job(job)

print("\nTITLE:")
print(enriched_job["title"])

print("\nCOMPANY:")
print(enriched_job["company"])

print("\nURL:")
print(enriched_job["url"])

print("\nDESCRIPTION LENGTH:")
print(len(
    enriched_job["full_description"]
))