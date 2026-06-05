import asyncio
from tools.job_details_scraper import (
    get_job_description,
    get_job_descriptions
)


def enrich_job(job):

    full_description = asyncio.run(get_job_description(
        job["url"]
    ))

    enriched_job = {
        **job,
        "full_description": full_description
    }

    return enriched_job


def enrich_jobs(jobs):
    job_urls = [
        job.get("url", "")
        for job in jobs
        if job.get("url")
    ]
    descriptions = asyncio.run(get_job_descriptions(job_urls))

    enriched_jobs = []

    for job in jobs:

        full_description = descriptions.get(
            job.get("url", ""),
            job.get("description", "")
        )

        enriched_jobs.append(
            {
                **job,
                "full_description": full_description or job.get("description", "")
            }
        )

    return enriched_jobs
