from a2a.server.agent_execution import AgentExecutor
from a2a.server.agent_execution.context import RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_agent_text_message
import json

from agents.cover_letter_agent import generate_cover_letter
from agents.resume_agent import tailor_resume
from agents.visa_agent import check_visa_eligibility
from tools.job_details_scraper import get_job_description, get_job_descriptions
from tools.seek_scraper import search_seek


class JobAssistantAgentExecutor(AgentExecutor):

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        # Parse the user input to extract action and params
        try:
            user_input = context.get_user_input()
            if isinstance(user_input, str):
                payload = json.loads(user_input)
            else:
                payload = user_input
            
            skill_id = payload.get("action")
            params = payload.get("params", {})
        except Exception as e:
            await event_queue.enqueue_event(new_agent_text_message(f"Error parsing request: {e}"))
            return

        if skill_id == "generate_cover_letter":
            cover_letter = generate_cover_letter(
                resume_text=params.get("resume_text", ""),
                job_description=params.get("job_description", ""),
                company=params.get("company", ""),
                title=params.get("title", ""),
            )
            await event_queue.enqueue_event(new_agent_text_message(cover_letter))

        elif skill_id == "scrape_job_description":
            job_description = await get_job_description(
                job_url=params.get("url", ""),
            )
            await event_queue.enqueue_event(new_agent_text_message(job_description))

        elif skill_id == "scrape_multiple_job_descriptions":
            job_descriptions = await get_job_descriptions(
                job_urls=params.get("urls", []),
            )
            await event_queue.enqueue_event(new_agent_text_message(str(job_descriptions)))

        elif skill_id == "generate_tailored_resume":
            tailored_resume = tailor_resume(
                resume_text=params.get("resume_text", ""),
                job_description=params.get("job_description", ""),
            )
            await event_queue.enqueue_event(new_agent_text_message(tailored_resume))

        elif skill_id == "search_jobs":
            jobs = await search_seek(
                role=params.get("role", ""),
                location=params.get("location", ""),
            )
            await event_queue.enqueue_event(new_agent_text_message(str(jobs)))

        elif skill_id == "check_visa_eligibility":
            visa_result = check_visa_eligibility(
                full_description=params.get("job_description", ""),
                visa_type=params.get("visa_type", ""),
            )
            await event_queue.enqueue_event(new_agent_text_message(str(visa_result)))

        else:
            await event_queue.enqueue_event(new_agent_text_message(f"Unknown skill: {skill_id}"))

    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        raise Exception("Cancel not supported")