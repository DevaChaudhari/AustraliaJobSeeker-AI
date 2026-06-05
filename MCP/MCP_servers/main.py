import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


from fastmcp import FastMCP
from agents.cover_letter_agent import generate_cover_letter
from tools.job_details_scraper import get_job_description, get_job_descriptions
from agents.resume_agent import tailor_resume
from tools.seek_scraper import search_seek
from agents.visa_agent import check_visa_eligibility

mcp = FastMCP("Servers for cover letter generation, job details scraping, resume parsing, seek scraping")

@mcp.tool()
async def generate_job_cover_letter(
    resume_text: str,
    job_description: str,
    company: str,
    title: str
) -> dict:
    """
    Generate a cover letter for a specific job.
    """

    cover_letter = await generate_cover_letter(
        resume_text=resume_text,
        job_description=job_description,
        company=company,
        title=title
    )

    return {
        "cover_letter": cover_letter
    }

@mcp.tool()
async def scrape_job_description(url: str) -> dict:
    """
    Scrape the full job description from a single job URL.
    """

    description = await get_job_description(url)

    return {
        "url": url,
        "description": description
    }


@mcp.tool()
async def scrape_multiple_job_descriptions(urls: list[str]) -> dict:
    """
    Scrape full job descriptions for multiple job URLs.
    """

    descriptions = await get_job_descriptions(urls)

    return {
        "descriptions": descriptions,
        "count": len(descriptions)
    }

@mcp.tool()
async def generate_tailored_resume(resume_text: str, job_description: str) -> dict:
    """
    Generate a tailored resume for a job description.
    """

    tailored_resume = await tailor_resume(
        resume_text=resume_text,
        job_description=job_description
    )

    return {
        "tailored_resume": tailored_resume
    }

@mcp.tool()
async def search_jobs(role: str, location: str) -> dict:
    """
    Search SEEK jobs for a given role and location.
    """

    jobs = await search_seek(
        role=role,
        location=location
    )

    return {
        "jobs": jobs,
        "count": len(jobs)
    }

@mcp.tool()
async def check_job_visa_eligibility(job_description: str, visa_type: str) -> dict:
    """
    Check whether a job is suitable for the selected Australian visa type.
    """

    return await check_visa_eligibility(
        full_description=job_description,
        visa_type=visa_type
    )

