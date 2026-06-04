from tools.seek_scraper import search_seek
from tools.job_details_scraper import (
    get_job_description
)

jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

job = jobs[0]

print("TITLE:")
print(job["title"])

print("\nURL:")
print(job["url"])

description = get_job_description(
    job["url"]
)

print("\nFULL DESCRIPTION PREVIEW:\n")

print(description[:3000])