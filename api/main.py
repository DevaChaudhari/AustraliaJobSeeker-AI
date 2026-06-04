from fastapi import FastAPI
import os
from dotenv import load_dotenv
load_dotenv()
from agents.supervisor_graph import graph
from agents.ranking_agent import rank_jobs
from agents.resume_agent import tailor_resume
from agents.cover_letter_agent import generate_cover_letter
from Langsmith.integration import get_graph_config


app = FastAPI(title="AustraliaJobSeeker AI")


def _env_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default

    return max(value, 0)


MAX_RESPONSE_JOBS = _env_int("MAX_RESPONSE_JOBS", 10)


def _load_default_resume() -> str:
    with open("data/sample_resume.txt", "r", encoding="utf-8") as f:
        return f.read()


def _normalise_reasons(reasons):
    if not reasons:
        return []
    if isinstance(reasons, list):
        return [str(reason).strip() for reason in reasons if str(reason).strip()]
    return [str(reasons).strip()]


def _is_visa_suitable(job: dict) -> bool:
    visa_result = job.get("visa_result", {})
    if visa_result.get("status"):
        return visa_result.get("status") == "likely_eligible"
    return visa_result.get("eligible") is True


@app.get("/")
def home():

    return {
        "message": "AustraliaJobSeeker AI Running"
    }


@app.get("/health")
def health():
    return {"status": "ok", "detail": "Backend healthy"}


@app.post("/search-jobs")
def search_jobs(data: dict):
    role = data["role"]
    location = data["location"]
    visa_type = data["visa_type"]
    resume_text = (data.get("resume_text") or "").strip()
    has_resume = bool(resume_text)
    config = get_graph_config()

    result = graph.invoke(
        {
            "role": role,
            "location": location,
            "visa_type": visa_type,
            "jobs": []
        },
        config=config,
    )

    ranked_jobs = rank_jobs(result["jobs"], resume_text)
    visa_suitable_jobs = [job for job in ranked_jobs if _is_visa_suitable(job)]
    response_jobs = []

    for job in visa_suitable_jobs[:MAX_RESPONSE_JOBS]:
        visa_result = job.get("visa_result", {})
        profile_result = job.get("profile_result", {})
        eligibility_status = visa_result.get(
            "status",
            "likely_eligible" if visa_result.get("eligible") else "restricted"
        )
        eligibility_reasons = _normalise_reasons(visa_result.get("reasons"))

        response_jobs.append(
            {
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "score": profile_result.get("match_score") if has_resume else None,
                "score_available": has_resume,
                "matched_skills": profile_result.get("matched_skills", []),
                "missing_skills": profile_result.get("missing_skills", []),
                "eligible": visa_result.get("eligible", False),
                "eligibility_status": eligibility_status,
                "eligibility_label": visa_result.get("label", eligibility_status.replace("_", " ").title()),
                "eligibility_reasons": eligibility_reasons,
                "eligibility_reason": " ".join(eligibility_reasons),
                "eligibility_source": visa_result.get("source", "unknown"),
                "url": job["url"],
                "description": job["full_description"]
            }
        )

    return {
        "total_jobs": len(response_jobs),
        "total_scanned_jobs": len(ranked_jobs),
        "filtered_out_jobs": len(ranked_jobs) - len(visa_suitable_jobs),
        "score_available": has_resume,
        "jobs": response_jobs
    }


@app.post("/generate-resume")
def generate_resume(data: dict):
    resume_text = data.get("resume_text") or _load_default_resume()

    tailored_resume = tailor_resume(
        resume_text=resume_text,
        job_description=data["job_description"]
    )

    return {"resume": tailored_resume}


@app.post("/generate-cover-letter")
def create_cover_letter(data: dict):
    resume_text = data.get("resume_text") or _load_default_resume()

    cover_letter = generate_cover_letter(
        resume_text=resume_text,
        job_description=data["job_description"],
        company=data["company"],
        title=data["title"]
    )

    return {"cover_letter": cover_letter}

