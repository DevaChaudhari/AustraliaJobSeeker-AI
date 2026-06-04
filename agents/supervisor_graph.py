from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from tools.seek_scraper import search_seek
from agents.job_enrichment_agent import enrich_jobs
from agents.visa_agent import check_visa_eligibility


class JobState(TypedDict):
    role: str
    location: str
    visa_type: str
    jobs: list


def search_node(state: JobState):

    jobs = search_seek(
        role=state["role"],
        location=state["location"]
    )

    return {
        **state,
        "jobs": jobs
    }


def enrich_node(state: JobState):

    enriched_jobs = enrich_jobs(
        state["jobs"]
    )

    return {
        **state,
        "jobs": enriched_jobs
    }


def visa_node(state: JobState):

    processed_jobs = []

    for job in state["jobs"]:

        visa_result = check_visa_eligibility(
            job["full_description"],
            state["visa_type"]
        )

        job["visa_result"] = visa_result

        processed_jobs.append(job)

    return {
        **state,
        "jobs": processed_jobs
    }


graph_builder = StateGraph(JobState)

graph_builder.add_node(
    "search",
    search_node
)

graph_builder.add_node(
    "enrich",
    enrich_node
)

graph_builder.add_node(
    "visa",
    visa_node
)

graph_builder.add_edge(
    START,
    "search"
)

graph_builder.add_edge(
    "search",
    "enrich"
)

graph_builder.add_edge(
    "enrich",
    "visa"
)

graph_builder.add_edge(
    "visa",
    END
)

graph = graph_builder.compile()
