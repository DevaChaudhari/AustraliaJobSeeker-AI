import httpx
import asyncio
import uuid
import json

from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types import TransportProtocol, Message, Role, Part, TextPart


BASE_URL = "http://localhost:9999/"


def build_message(action: str, params: dict) -> Message:
    """Helper to build an A2A Message with action + params as JSON text."""
    payload = json.dumps({"action": action, "params": params})
    return Message(
        role=Role.user,
        message_id=str(uuid.uuid4()),
        parts=[Part(root=TextPart(text=payload))],
    )


async def main():
    # Increase timeouts to accommodate potentially long-running skill executions
    timeout = httpx.Timeout(60.0, connect=10.0, read=60.0)
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:

        # ── Resolve Agent Card ─────────────────────────────────────────
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=BASE_URL)
        agent_card = await resolver.get_agent_card()
        print("Agent Card:", agent_card.model_dump_json(indent=2))

        # ── Initialize A2A Client ──────────────────────────────────────
        factory = ClientFactory(
            ClientConfig(
                httpx_client=httpx_client,
                supported_transports=[TransportProtocol.jsonrpc],
            )
        )
        a2a_client = factory.create(agent_card)
        print("A2A Client Initialized\n")

        # ── 1. Search Jobs on SEEK ─────────────────────────────────────
        print("=" * 60)
        print("SKILL: Search Jobs on SEEK")
        print("=" * 60)
        message = build_message(
            action="search_jobs",
            params={
                "role": "Data Engineer",
                "location": "Melbourne",
            },
        )
        async for event in a2a_client.send_message(message):
            print("Response:", event.model_dump_json(indent=2))

        # ── 2. Scrape Single Job Description ───────────────────────────
        print("=" * 60)
        print("SKILL: Scrape Single Job Description")
        print("=" * 60)
        message = build_message(
            action="scrape_job_description",
            params={
                "url": "https://au.seek.com/job/92194846",
            },
        )
        async for event in a2a_client.send_message(message):
            print("Response:", event.model_dump_json(indent=2))

        # ── 3. Scrape Multiple Job Descriptions ────────────────────────
        print("=" * 60)
        print("SKILL: Scrape Multiple Job Descriptions")
        print("=" * 60)
        message = build_message(
            action="scrape_multiple_job_descriptions",
            params={
                "urls": [
                    "https://au.seek.com/job/92194846",
                    "https://au.seek.com/job/87654321",
                ],
            },
        )
        async for event in a2a_client.send_message(message):
            print("Response:", event.model_dump_json(indent=2))

        # ── 4. Generate Cover Letter ───────────────────────────────────
        print("=" * 60)
        print("SKILL: Generate Cover Letter")
        print("=" * 60)
        message = build_message(
            action="generate_cover_letter",
            params={
                "resume_text": "John Doe | 5 years Python experience | AWS certified...",
                "job_description": "We are looking for a Data Engineer with Python and AWS skills...",
                "company": "Atlassian",
                "title": "Senior Data Engineer",
            },
        )
        async for event in a2a_client.send_message(message):
            print("Response:", event.model_dump_json(indent=2))

        # ── 5. Generate Tailored Resume ────────────────────────────────
        print("=" * 60)
        print("SKILL: Generate Tailored Resume")
        print("=" * 60)
        message = build_message(
            action="generate_tailored_resume",
            params={
                "resume_text": "John Doe | 5 years Python experience | AWS certified...",
                "job_description": "We are looking for a Data Engineer with Python and AWS skills...",
            },
        )
        async for event in a2a_client.send_message(message):
            print("Response:", event.model_dump_json(indent=2))

        # ── 6. Check Visa Eligibility ──────────────────────────────────
        print("=" * 60)
        print("SKILL: Check Visa Eligibility")
        print("=" * 60)
        message = build_message(
            action="check_visa_eligibility",
            params={
                "job_description": "We are looking for a Data Engineer with Python and AWS skills...",
                "visa_type": "485",
            },
        )
        async for event in a2a_client.send_message(message):
            print("Response:", event.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())