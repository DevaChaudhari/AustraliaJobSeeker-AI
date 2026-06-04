from typing import TypedDict
import json

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from tools.mcp_client import call_mcp

# MCP Server endpoints
SEEK_MCP_URL = "http://127.0.0.1:9001"
RESUME_MCP_URL = "http://127.0.0.1:9002"
COVER_MCP_URL = "http://127.0.0.1:9003"
CHROMA_MCP_URL = "http://127.0.0.1:9004"


class JobState(TypedDict):

    role: str

    location: str

    visa_type: str

    resume_text: str

    jobs: list
    
    tailored_resumes: dict
    
    cover_letters: dict


def search_node(
    state: JobState
):
    # Call Seek MCP server for job search
    mcp_result = call_mcp(
        base_url=SEEK_MCP_URL,
        input_payload={
            "role": state["role"],
            "location": state["location"]
        },
        timeout=30
    )

    jobs = []
    if mcp_result.get("status") == "ok":
        jobs = mcp_result.get("result", {}).get("jobs", [])
    else:
        print(f"Seek MCP error: {mcp_result.get('error')}")

    return {
        **state,
        "jobs": jobs
    }


def visa_node(
    state: JobState
):

    processed_jobs = []

    for job in state["jobs"]:

        # Call ChromaDB MCP server for visa eligibility
        mcp_result = call_mcp(
            base_url=CHROMA_MCP_URL,
            input_payload={
                "job_description": job.get("full_description", ""),
                "visa_type": state.get("visa_type", "485")
            },
            timeout=15
        )

        # Parse LLM output if available
        visa_result = None
        if mcp_result.get("status") == "ok":
            llm_output = mcp_result.get("result", {}).get("llm_output", "")
            retrieved = mcp_result.get("result", {}).get("retrieved", [])
            
            # Try to parse LLM output as JSON
            try:
                visa_result = json.loads(llm_output)
            except (json.JSONDecodeError, TypeError):
                visa_result = {
                    "eligible": False,
                    "reason": llm_output,
                    "citations": [r.get("id") for r in retrieved]
                }
        else:
            visa_result = {
                "eligible": False,
                "reason": mcp_result.get("error", "Visa check failed"),
                "citations": []
            }

        job["visa_result"] = visa_result

        processed_jobs.append(
            job
        )

    return {
        **state,
        "jobs": processed_jobs
    }


def resume_tailor_node(
    state: JobState
):
    """Tailor resume for each eligible job"""
    
    tailored_resumes = {}
    
    for job in state["jobs"]:
        job_id = job.get("id", job.get("title", ""))
        
        # Only tailor if visa eligible
        is_eligible = job.get("visa_result", {}).get("eligible", False)
        if not is_eligible:
            continue
        
        # Call Resume Tailor MCP server
        mcp_result = call_mcp(
            base_url=RESUME_MCP_URL,
            input_payload={
                "resume_text": state["resume_text"],
                "job_description": job.get("full_description", "")
            },
            timeout=30
        )
        
        if mcp_result.get("status") == "ok":
            tailored = mcp_result.get("result", {}).get("tailored_resume", "")
            tailored_resumes[job_id] = tailored
        else:
            print(f"Resume tailor MCP error for job {job_id}: {mcp_result.get('error')}")
            tailored_resumes[job_id] = state["resume_text"]  # fallback to original
    
    return {
        **state,
        "tailored_resumes": tailored_resumes
    }


def cover_letter_node(
    state: JobState
):
    """Generate cover letters for eligible jobs"""
    
    cover_letters = {}
    
    for job in state["jobs"]:
        job_id = job.get("id", job.get("title", ""))
        
        # Only generate if visa eligible
        is_eligible = job.get("visa_result", {}).get("eligible", False)
        if not is_eligible:
            continue
        
        # Get tailored resume for this job
        tailored_resume = state["tailored_resumes"].get(job_id, state["resume_text"])
        
        # Call Cover Letter MCP server
        mcp_result = call_mcp(
            base_url=COVER_MCP_URL,
            input_payload={
                "resume_text": tailored_resume,
                "job_description": job.get("full_description", "")
            },
            timeout=30
        )
        
        if mcp_result.get("status") == "ok":
            cover = mcp_result.get("result", {}).get("cover_letter", "")
            cover_letters[job_id] = cover
        else:
            print(f"Cover letter MCP error for job {job_id}: {mcp_result.get('error')}")
            cover_letters[job_id] = ""  # empty fallback
    
    return {
        **state,
        "cover_letters": cover_letters
    }


def rank_node(
    state: JobState
):
    """Rank jobs by eligibility and match score"""
    
    eligible_jobs = [j for j in state["jobs"] if j.get("visa_result", {}).get("eligible", False)]
    ineligible_jobs = [j for j in state["jobs"] if not j.get("visa_result", {}).get("eligible", False)]
    
    ranked_jobs = eligible_jobs + ineligible_jobs

    return {
        **state,
        "jobs": ranked_jobs
    }


builder = StateGraph(
    JobState
)

builder.add_node(
    "search",
    search_node
)

builder.add_node(
    "visa",
    visa_node
)

builder.add_node(
    "resume_tailor",
    resume_tailor_node
)

builder.add_node(
    "cover_letter",
    cover_letter_node
)

builder.add_node(
    "rank",
    rank_node
)

builder.add_edge(
    START,
    "search"
)

builder.add_edge(
    "search",
    "visa"
)

builder.add_edge(
    "visa",
    "resume_tailor"
)

builder.add_edge(
    "resume_tailor",
    "cover_letter"
)

builder.add_edge(
    "cover_letter",
    "rank"
)

builder.add_edge(
    "rank",
    END
)

graph = builder.compile()