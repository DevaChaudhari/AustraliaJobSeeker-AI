import os

from playwright.async_api import async_playwright


def _env_int(name: str, default: int):
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default

    return max(value, 0)


async def _read_job_description(page, job_url: str):
    if not job_url:
        return ""

    await page.goto(
        job_url,
        timeout=60000,
        wait_until="domcontentloaded"
    )

    await page.wait_for_timeout(
        _env_int("JOB_DETAIL_WAIT_MS", 2000)
    )

    return await page.inner_text("body")


async def get_job_description(job_url: str):

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        text = await _read_job_description(page, job_url)

        await browser.close()

        return text


async def get_job_descriptions(job_urls: list[str]):
    descriptions = {}

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        for job_url in job_urls:

            try:

                descriptions[job_url] = await _read_job_description(
                    page,
                    job_url
                )

            except Exception as e:
                print(e)
                descriptions[job_url] = ""

        await browser.close()

    return descriptions
