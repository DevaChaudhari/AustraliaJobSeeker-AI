from a2a.types import AgentCard, AgentSkill, AgentCapabilities
import uvicorn


def main():

    # ── Agent Skills ───────────────────────────────────────────────────────────

    cover_letter_skill = AgentSkill(
        id="generate_cover_letter",
        name="Generate Cover Letter",
        description="Generate a tailored cover letter based on a resume and job description",
        tags=["cover letter", "resume", "job application", "writing"],
        examples=[
            "Generate a cover letter for a Software Engineer role at Google",
            "Write a cover letter using my resume for this job description",
        ],
    )

    scrape_job_skill = AgentSkill(
        id="scrape_job_description",
        name="Scrape Job Description",
        description="Scrape the full job description from a single job listing URL",
        tags=["scraping", "job description", "url", "seek"],
        examples=[
            "Get the job description from this URL",
            "Scrape this job listing for me",
        ],
    )

    scrape_multiple_jobs_skill = AgentSkill(
        id="scrape_multiple_job_descriptions",
        name="Scrape Multiple Job Descriptions",
        description="Scrape full job descriptions from multiple job listing URLs at once",
        tags=["scraping", "bulk", "job description", "multiple urls"],
        examples=[
            "Scrape all these job listings for me",
            "Get job descriptions from these 5 URLs",
        ],
    )

    tailored_resume_skill = AgentSkill(
        id="generate_tailored_resume",
        name="Generate Tailored Resume",
        description="Tailor an existing resume to match a specific job description",
        tags=["resume", "tailoring", "job application", "writing"],
        examples=[
            "Tailor my resume for this job description",
            "Rewrite my resume to match this role",
        ],
    )

    search_jobs_skill = AgentSkill(
        id="search_jobs",
        name="Search Jobs on SEEK",
        description="Search for jobs on SEEK by role and location",
        tags=["seek", "job search", "jobs", "Australia"],
        examples=[
            "Search for Data Engineer jobs in Melbourne",
            "Find Software Developer roles in Sydney on SEEK",
        ],
    )

    visa_eligibility_skill = AgentSkill(
        id="check_visa_eligibility",
        name="Check Visa Eligibility",
        description="Check whether a job is suitable for a specific Australian visa type",
        tags=["visa", "eligibility", "Australia", "immigration", "work rights"],
        examples=[
            "Is this job eligible for a 485 visa holder?",
            "Can I apply for this role on a student visa?",
        ],
    )

    # ── Agent Card ─────────────────────────────────────────────────────────────

    agent_card = AgentCard(
        name="Job Assistant Agent",
        description=(
            "An intelligent job assistant that helps with cover letter generation, "
            "resume tailoring, job scraping from listing URLs, SEEK job search, "
            "and Australian visa eligibility checks."
        ),
        url="http://localhost:9999/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[
            cover_letter_skill,
            scrape_job_skill,
            scrape_multiple_jobs_skill,
            tailored_resume_skill,
            search_jobs_skill,
            visa_eligibility_skill,
        ],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    # ── Request Handler ────────────────────────────────────────────────────────

    from a2a.server.request_handlers import DefaultRequestHandler
    from .agent_executor import JobAssistantAgentExecutor
    from a2a.server.tasks import InMemoryTaskStore

    request_handler = DefaultRequestHandler(
        agent_executor=JobAssistantAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # ── Server ─────────────────────────────────────────────────────────────────

    from a2a.server.apps import A2AStarletteApplication

    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()