import os
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from australiajobseeker.agents.cover_letter_agent import generate_cover_letter
from australiajobseeker.agents.ranking_agent import rank_jobs
from australiajobseeker.agents.resume_agent import tailor_resume
from australiajobseeker.agents.supervisor_graph import graph
from australiajobseeker.observability import get_graph_config

load_dotenv()

app = FastAPI(title="AustraliaJobSeeker AI")

# Comma-separated list of allowed browser origins, e.g. the Amplify app URL.
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _env_int(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default

    return max(value, 0)


MAX_RESPONSE_JOBS = _env_int("MAX_RESPONSE_JOBS", 10)
DEFAULT_RESUME_PATH = Path(__file__).resolve().parent.parent / "resources" / "sample_resume.txt"


def _load_default_resume() -> str:
    return DEFAULT_RESUME_PATH.read_text(encoding="utf-8")


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


def _run_search(data: dict) -> dict:
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


# Searches scrape and call an LLM per job, which can outlast CloudFront's 60s
# origin timeout. The async endpoints let the browser start a search and poll.
# State is in-memory, so this assumes a single running task.
_SEARCH_TTL_SECONDS = 3600
_search_executor = ThreadPoolExecutor(max_workers=2)
_search_jobs: dict[str, dict] = {}
_search_jobs_lock = threading.Lock()


def _prune_searches() -> None:
    cutoff = time.time() - _SEARCH_TTL_SECONDS
    with _search_jobs_lock:
        for job_id in [k for k, v in _search_jobs.items() if v["created"] < cutoff]:
            del _search_jobs[job_id]


def _search_worker(job_id: str, data: dict) -> None:
    try:
        result = _run_search(data)
        update = {"status": "done", "result": result}
    except Exception as e:
        traceback.print_exc()
        update = {"status": "error", "error": str(e)}
    with _search_jobs_lock:
        _search_jobs[job_id].update(update)


@app.post("/search-jobs")
def search_jobs(data: dict):
    return _run_search(data)


@app.post("/search-jobs/async", status_code=202)
def start_search_jobs(data: dict):
    missing = [f for f in ("role", "location", "visa_type") if f not in data]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {missing}")

    _prune_searches()
    job_id = uuid.uuid4().hex
    with _search_jobs_lock:
        _search_jobs[job_id] = {"status": "running", "created": time.time()}
    _search_executor.submit(_search_worker, job_id, data)
    return {"job_id": job_id, "status": "running"}


@app.get("/search-jobs/{job_id}")
def get_search_jobs(job_id: str):
    with _search_jobs_lock:
        job = _search_jobs.get(job_id)
        snapshot = dict(job) if job else None
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Search not found or expired")
    snapshot.pop("created", None)
    return snapshot


@app.post("/generate-resume")
def generate_resume(data: dict):
    try:
        resume_text = data.get("resume_text") or _load_default_resume()
        if "job_description" not in data:
            raise HTTPException(status_code=400, detail="job_description is required")
        
        tailored_resume = tailor_resume(
            resume_text=resume_text,
            job_description=data["job_description"]
        )
        return {"resume": tailored_resume}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/generate-cover-letter")
def create_cover_letter(data: dict):
    try:
        # Validate required fields
        required = ["job_description", "company", "title"]
        missing = [f for f in required if f not in data]
        if missing:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {missing}"
            )

        resume_text = data.get("resume_text") or _load_default_resume()

        cover_letter = generate_cover_letter(
            resume_text=resume_text,
            job_description=data["job_description"],
            company=data["company"],
            title=data["title"]
        )

        return {"cover_letter": cover_letter}

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

