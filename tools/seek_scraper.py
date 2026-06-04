import os
import re
from playwright.async_api import async_playwright

DEFAULT_MAX_SEEK_PAGES = 1
DEFAULT_MAX_SEEK_JOBS = 10
DEFAULT_SEEK_PAGE_WAIT_MS = 3000

AUSTRALIA_WIDE_LOCATIONS = {
    "all australia",
    "australia",
    "whole australia",
    "anywhere australia",
    "anywhere in australia",
    "national",
}

def _env_int(name: str, default: int):
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default

    return max(value, 0)


def _seek_slug(value: str, lowercase: bool = False):
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-")
    return slug.lower() if lowercase else slug


def _normalise_location(location: str):
    cleaned = (location or "").strip()
    key = re.sub(r"[^a-z0-9]+", " ", cleaned.lower()).strip()

    if key in AUSTRALIA_WIDE_LOCATIONS:
        return ""

    cleaned = re.sub(r",?\s*australia$", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = cleaned.replace(",", " ")
    return " ".join(cleaned.split())


def _build_search_url(role: str, location: str, page_number: int = 1):
    role_slug = _seek_slug(role, lowercase=True)
    location_query = _normalise_location(location)

    if location_query:
        location_slug = _seek_slug(location_query)
        base_url = f"https://au.seek.com/{role_slug}-jobs/in-{location_slug}"
    else:
        base_url = f"https://au.seek.com/{role_slug}-jobs"

    if page_number <= 1:
        return base_url

    return f"{base_url}?page={page_number}"


async def search_seek(role: str, location: str, max_pages: int = None, max_jobs: int = None):

    if max_pages is None:
        max_pages = _env_int("SEEK_MAX_PAGES", DEFAULT_MAX_SEEK_PAGES)
    if max_jobs is None:
        max_jobs = _env_int("SEEK_MAX_JOBS", DEFAULT_MAX_SEEK_JOBS)

    jobs = []
    seen_urls = set()

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        page_number = 1

        while max_pages == 0 or page_number <= max_pages:
            url = _build_search_url(role, location, page_number)

            await page.goto(
                url,
                timeout=60000
            )

            await page.wait_for_timeout(
                _env_int("SEEK_PAGE_WAIT_MS", DEFAULT_SEEK_PAGE_WAIT_MS)
            )

            articles = page.locator("article")
            article_count = await articles.count()

            if article_count == 0:
                break

            added_on_page = 0

            for i in range(article_count):

                if max_jobs and len(jobs) >= max_jobs:
                    break

                try:

                    article = articles.nth(i)

                    text = await article.inner_text()

                    lines = [
                        line.strip()
                        for line in text.split("\n")
                        if line.strip()
                    ]

                    title = ""
                    company = ""
                    location_text = ""
                    job_url = ""

                    # Extract title
                    for idx, line in enumerate(lines):

                        if (
                            "featured job" in line.lower()
                            or "listed" in line.lower()
                        ):

                            if idx + 1 < len(lines):
                                title = lines[idx + 1]
                                break

                    # Extract company
                    if "at" in lines:

                        at_index = lines.index("at")

                        if at_index + 1 < len(lines):
                            company = lines[at_index + 1]

                    # Extract location
                    states = [
                        "SA",
                        "NSW",
                        "VIC",
                        "QLD",
                        "WA",
                        "TAS",
                        "ACT",
                        "NT"
                    ]

                    for line in lines:

                        if any(
                            state in line
                            for state in states
                        ):
                            location_text = line
                            break

                    # Extract URL
                    try:

                        job_link = article.locator(
                            '[data-automation="jobTitle"]'
                        ).first

                        href = await job_link.get_attribute("href")

                        if href:

                            if href.startswith("/"):

                                job_url = (
                                    "https://au.seek.com"
                                    + href
                                )

                            else:

                                job_url = href

                    except:
                        pass

                    if job_url and job_url in seen_urls:
                        continue

                    if job_url:
                        seen_urls.add(job_url)

                    jobs.append(
                        {
                            "title": title,
                            "company": company,
                            "location": location_text,
                            "description": text,
                            "url": job_url
                        }
                    )
                    added_on_page += 1

                except Exception as e:
                    print(e)

            if max_jobs and len(jobs) >= max_jobs:
                break

            if added_on_page == 0:
                break

            page_number += 1

        await browser.close()

    return jobs
