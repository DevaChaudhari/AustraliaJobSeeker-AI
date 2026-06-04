"""
AustraliaJobSeeker AI - Production Frontend Application

A Streamlit application for finding visa-friendly AI jobs in Australia with
AI-powered resume and cover letter generation.
"""

import streamlit as st
import requests
import os
import logging
import time
from io import BytesIO
from typing import Optional, Dict, Any
from functools import wraps

# ============================================================================
# Configuration & Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Backend configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "300"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))

# API endpoints
HEALTH_API = f"{BACKEND_URL}/health" if hasattr(st, "_is_running_with_streamlit") else None
SEARCH_API = f"{BACKEND_URL}/search-jobs"
RESUME_API = f"{BACKEND_URL}/generate-resume"
COVER_API = f"{BACKEND_URL}/generate-cover-letter"

# UI Configuration
MAX_RESUME_LENGTH = 50000  # Characters
MAX_JOB_DESCRIPTION_LENGTH = 10000
SUPPORTED_RESUME_TYPES = ["txt", "docx", "pdf"]
VISA_TYPE_OPTIONS = {
    "500": "Student Visa (Subclass 500)",
    "485": "Temporary Graduate Visa (Subclass 485)",
    "482": "Temporary Skill Shortage / Sponsorship Visa (Subclass 482)",
    "PR": "Permanent Resident / Citizen (PR)",
}
LOCATION_OPTIONS = [
    "All Australia",
    "Sydney, NSW, Australia",
    "Melbourne, VIC, Australia",
    "Brisbane, QLD, Australia",
    "Perth, WA, Australia",
    "Adelaide, SA, Australia",
    "Canberra, ACT, Australia",
    "Hobart, TAS, Australia",
    "Darwin City, NT, Australia",
    "Gold Coast, QLD, Australia",
    "Newcastle, NSW, Australia",
    "Sunshine Coast, QLD, Australia",
    "Wollongong, NSW, Australia",
    "Geelong, VIC, Australia",
    "Townsville, QLD, Australia",
    "Cairns, QLD, Australia",
    "Toowoomba, QLD, Australia",
    "Ballarat, VIC, Australia",
    "Bendigo, VIC, Australia",
    "Launceston, TAS, Australia",
    "Mackay, QLD, Australia",
    "Rockhampton, QLD, Australia",
    "Bunbury, WA, Australia",
    "Albury, NSW, Australia",
    "Wagga Wagga, NSW, Australia",
    "Coffs Harbour, NSW, Australia",
    "Port Macquarie, NSW, Australia",
    "Tamworth, NSW, Australia",
    "Orange, NSW, Australia",
    "Dubbo, NSW, Australia",
    "Shepparton, VIC, Australia",
    "Mildura, VIC, Australia",
    "Warrnambool, VIC, Australia",
    "Traralgon, VIC, Australia",
    "Bundaberg, QLD, Australia",
    "Hervey Bay, QLD, Australia",
    "Gladstone, QLD, Australia",
    "Mount Gambier, SA, Australia",
    "Whyalla, SA, Australia",
    "Albany, WA, Australia",
    "Geraldton, WA, Australia",
    "Kalgoorlie, WA, Australia",
    "Broome, WA, Australia",
    "Alice Springs, NT, Australia",
]

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AustraliaJobSeeker AI",
    page_icon="🇦🇺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Utility Functions
# ============================================================================

def retry_with_exponential_backoff(max_retries: int = MAX_RETRIES):
    """Decorator for retrying API requests with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        wait_time = RETRY_DELAY * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s..."
                        )
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} attempts failed: {e}")
                        raise
        return wrapper
    return decorator


def is_backend_healthy() -> bool:
    """Check if the backend is reachable."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except Exception as e:
        logger.warning(f"Backend health check failed: {e}")
        return False


def validate_resume_text(text: str) -> tuple[bool, str]:
    """Validate uploaded resume text."""
    if not text or not text.strip():
        return False, "Resume is empty."
    if len(text) > MAX_RESUME_LENGTH:
        return False, f"Resume exceeds {MAX_RESUME_LENGTH} characters."
    if len(text.split()) < 10:
        return False, "Resume is too short (minimum 10 words)."
    return True, ""


def validate_job_search_inputs(role: str, location: Optional[str], visa_type: Optional[str]) -> tuple[bool, str]:
    """Validate job search input parameters."""
    if not role or not role.strip():
        return False, "Job role is required."
    if not location or not location.strip():
        return False, "Location is required."
    if not visa_type:
        return False, "Visa type is required."
    if len(role) > 100:
        return False, "Job role is too long (max 100 characters)."
    if len(location) > 100:
        return False, "Location is too long (max 100 characters)."
    return True, ""


def extract_docx_text(file_bytes: bytes) -> Optional[str]:
    """Extract text from .docx file."""
    try:
        from docx import Document
    except ImportError:
        return None

    try:
        document = Document(BytesIO(file_bytes))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        text = "\n\n".join(paragraphs)
        logger.info(f"Extracted {len(text)} characters from DOCX")
        return text if text else None
    except Exception as e:
        logger.error(f"Failed to extract text from DOCX: {e}")
        return None


def extract_pdf_text(file_bytes: bytes) -> Optional[str]:
    """Extract text from a selectable-text PDF file."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None

    try:
        reader = PdfReader(BytesIO(file_bytes))
        page_texts = []

        for page in reader.pages:
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            if page_text:
                page_texts.append(page_text)

        text = "\n\n".join(page_texts)
        logger.info(f"Extracted {len(text)} characters from PDF")
        return text if text else None
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return None


def extract_txt_text(file_bytes: bytes) -> Optional[str]:
    """Extract text from .txt file."""
    try:
        text = file_bytes.decode("utf-8", errors="ignore").strip()
        logger.info(f"Extracted {len(text)} characters from TXT")
        return text if text else None
    except Exception as e:
        logger.error(f"Failed to extract text from TXT: {e}")
        return None


@retry_with_exponential_backoff()
def search_jobs(
    role: str,
    location: str,
    visa_type: str,
    resume_text: Optional[str] = None
) -> Dict[str, Any]:
    """Search for visa-friendly jobs."""
    payload = {
        "role": role.strip(),
        "location": location.strip(),
        "visa_type": visa_type,
        "resume_text": resume_text
    }
    logger.info(f"Searching jobs: role={role}, location={location}, visa_type={visa_type}")
    
    response = requests.post(
        SEARCH_API,
        json=payload,
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


@retry_with_exponential_backoff()
def generate_resume(
    job_description: str,
    resume_text: str
) -> Dict[str, Any]:
    """Generate tailored resume."""
    payload = {
        "job_description": job_description[:MAX_JOB_DESCRIPTION_LENGTH],
        "resume_text": resume_text
    }
    logger.info("Generating tailored resume")
    
    response = requests.post(
        RESUME_API,
        json=payload,
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


@retry_with_exponential_backoff()
def generate_cover_letter(
    job_description: str,
    company: str,
    title: str,
    resume_text: str
) -> Dict[str, Any]:
    """Generate customized cover letter."""
    payload = {
        "job_description": job_description[:MAX_JOB_DESCRIPTION_LENGTH],
        "company": company,
        "title": title,
        "resume_text": resume_text
    }
    logger.info(f"Generating cover letter for {company} - {title}")
    
    response = requests.post(
        COVER_API,
        json=payload,
        timeout=API_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


# ============================================================================
# UI Components
# ============================================================================

def render_header():
    """Render application header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🇦🇺 AustraliaJobSeeker AI")
        st.markdown(
            "Find visa-friendly AI jobs in Australia with AI-powered resume and "
            "cover letter generation."
        )
    with col2:
        # Backend status indicator
        if is_backend_healthy():
            st.success("✅ Backend Online")
        else:
            st.error("❌ Backend Offline")


def render_resume_uploader():
    """Render resume upload section."""
    st.subheader("📄 Your Resume")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload resume (.txt, .docx, or .pdf)",
            type=SUPPORTED_RESUME_TYPES,
            help="Maximum 50,000 characters. PDFs must contain selectable text."
        )
    
    with col2:
        if "resume_text" in st.session_state:
            st.metric(
                "Characters",
                len(st.session_state["resume_text"])
            )
    
    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name.lower()

            if file_name.endswith(".docx"):
                resume_text = extract_docx_text(file_bytes)
                if resume_text is None:
                    st.error(
                        "Failed to extract DOCX. Install with: `pip install python-docx`"
                    )
                    return
            elif file_name.endswith(".pdf"):
                resume_text = extract_pdf_text(file_bytes)
                if resume_text is None:
                    st.error(
                        "Failed to extract PDF text. Install with: `pip install pypdf`, "
                        "and make sure the PDF contains selectable text."
                    )
                    return
            else:
                resume_text = extract_txt_text(file_bytes)
                if resume_text is None:
                    st.error("Failed to extract TXT file.")
                    return
            
            # Validate resume
            is_valid, error_msg = validate_resume_text(resume_text)
            if not is_valid:
                st.error(f"Resume validation failed: {error_msg}")
                return
            
            st.session_state["resume_text"] = resume_text
            st.success("✅ Resume uploaded successfully")
            
            with st.expander("📋 Preview Resume"):
                st.text_area(
                    "Resume Content",
                    resume_text,
                    height=200,
                    disabled=True
                )
        except Exception as e:
            logger.error(f"Resume upload failed: {e}")
            st.error(f"Upload failed: {str(e)}")


def render_search_form():
    """Render job search form."""
    st.subheader("🔍 Search Jobs")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        role = st.text_input(
            "Job Role",
            placeholder="e.g., AI Engineer, ML Developer",
            help="e.g., AI Engineer, ML Developer"
        )
    
    with col2:
        location = st.selectbox(
            "Location",
            LOCATION_OPTIONS,
            index=None,
            placeholder="Search cities, regions or countries",
            help="Search or select a city, region, state, or All Australia",
            accept_new_options=True,
            filter_mode="fuzzy"
        )
    
    with col3:
        visa_type = st.selectbox(
            "Visa Type",
            list(VISA_TYPE_OPTIONS.keys()),
            format_func=lambda visa: VISA_TYPE_OPTIONS.get(visa, visa),
            index=None,
            placeholder="Select visa type",
            help="Select the visa subclass/name that applies to you"
        )
    
    return role, location, visa_type


def format_eligibility_reason(job: Dict[str, Any]) -> str:
    """Return a readable visa eligibility reason for display."""
    reasons = job.get("eligibility_reasons") or []
    if isinstance(reasons, list) and reasons:
        return " ".join(str(reason).strip() for reason in reasons if str(reason).strip())
    return str(job.get("eligibility_reason") or "").strip()


def render_eligibility_status(job: Dict[str, Any]):
    """Render a visa status that distinguishes certainty from unknowns."""
    status = job.get("eligibility_status")
    if not status:
        status = "likely_eligible" if job.get("eligible", False) else "restricted"

    label = job.get("eligibility_label") or status.replace("_", " ").title()
    reason = format_eligibility_reason(job)
    source = job.get("eligibility_source", "unknown")

    if status == "likely_eligible":
        st.success(f"✅ {label}")
    elif status == "restricted":
        st.error(f"❌ {label}")
    else:
        st.warning(f"⚠️ {label}")

    if reason:
        st.caption(f"Reason: {reason}")
    if source and source != "unknown":
        st.caption(f"Source: {source.replace('_', ' ')}")


def render_match_score(job: Dict[str, Any]):
    """Render resume match only when a user resume was used."""
    score = job.get("score")

    if not job.get("score_available") or score is None:
        st.caption("Resume Match")
        st.info("Upload resume to calculate")
        return

    if isinstance(score, float):
        score_text = f"{score:.0%}" if score <= 1 else f"{score:.0f}%"
    else:
        score_text = f"{score}%"

    st.metric("Resume Match", score_text)


def is_visa_suitable_job(job: Dict[str, Any]) -> bool:
    """Only show jobs that satisfy the selected visa conditions."""
    if job.get("eligibility_status"):
        return job.get("eligibility_status") == "likely_eligible"
    return job.get("eligible") is True


def render_job_results(jobs: list):
    """Render job search results."""
    jobs = [job for job in jobs if is_visa_suitable_job(job)]

    if not jobs:
        filtered_count = st.session_state.get("filtered_out_jobs", 0)
        if filtered_count:
            st.warning(
                f"No visa-suitable jobs found. {filtered_count} jobs were hidden "
                "because they were restricted or unknown for the selected visa."
            )
        else:
            st.warning("No visa-suitable jobs found matching your criteria.")
        return

    st.subheader(f"📊 Found {len(jobs)} Jobs")
    total_scanned = st.session_state.get("total_scanned_jobs")
    filtered_count = st.session_state.get("filtered_out_jobs", 0)

    if total_scanned:
        st.caption(
            f"Showing {len(jobs)} visa-suitable jobs from {total_scanned} scanned. "
            f"Hidden: {filtered_count} restricted or unknown."
        )
    
    for job_idx, job in enumerate(jobs):
        with st.container(border=True):
            # Job header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {job.get('title', 'Untitled')}")
                st.markdown(f"**{job.get('company', 'Unknown Company')}** · {job.get('location', 'N/A')}")
            with col2:
                render_match_score(job)
            
            # Visa eligibility
            col1, col2 = st.columns(2)
            with col1:
                render_eligibility_status(job)
            with col2:
                if job.get("url"):
                    st.markdown(f"[🔗 View Full Job]({job['url']})")
            
            # Job description preview
            description = job.get("description", "")
            if description:
                with st.expander("📝 Job Description"):
                    st.write(description[:500] + "..." if len(description) > 500 else description)
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(
                    "📄 Generate Tailored Resume",
                    key=f"resume_{job_idx}",
                    help="Generate resume tailored to this job"
                ):
                    if "resume_text" not in st.session_state:
                        st.error("Please upload your resume first.")
                    else:
                        render_resume_generation(job, job_idx)
            
            with col2:
                if st.button(
                    "💌 Generate Cover Letter",
                    key=f"cover_{job_idx}",
                    help="Generate cover letter for this job"
                ):
                    if "resume_text" not in st.session_state:
                        st.error("Please upload your resume first.")
                    else:
                        render_cover_letter_generation(job, job_idx)
            
            st.divider()


def render_resume_generation(job: Dict[str, Any], job_idx: int):
    """Handle resume generation."""
    try:
        with st.spinner("✨ Generating tailored resume..."):
            resume_result = generate_resume(
                job_description=job.get("description", ""),
                resume_text=st.session_state["resume_text"]
            )
        
        resume = resume_result.get("resume")
        if resume:
            st.success("Resume generated successfully!")
            st.text_area(
                "Tailored Resume",
                resume,
                height=300,
                disabled=True,
                key=f"resume_output_{job_idx}"
            )
            st.download_button(
                "⬇️ Download Resume",
                resume,
                file_name=f"tailored_resume_{job_idx}.txt",
                mime="text/plain",
                key=f"download_resume_{job_idx}"
            )
        else:
            st.error("Resume generation returned no content.")
    
    except requests.exceptions.Timeout:
        st.error(f"Resume generation timed out (>{API_TIMEOUT}s). Please try again.")
        logger.error("Resume generation timeout")
    except requests.exceptions.RequestException as e:
        st.error(f"Resume generation failed: {str(e)}")
        logger.error(f"Resume generation error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error in resume generation: {e}")


def render_cover_letter_generation(job: Dict[str, Any], job_idx: int):
    """Handle cover letter generation."""
    try:
        with st.spinner("✨ Generating cover letter..."):
            cover_result = generate_cover_letter(
                job_description=job.get("description", ""),
                company=job.get("company", ""),
                title=job.get("title", ""),
                resume_text=st.session_state["resume_text"]
            )
        
        cover_letter = cover_result.get("cover_letter")
        if cover_letter:
            st.success("Cover letter generated successfully!")
            st.text_area(
                "Cover Letter",
                cover_letter,
                height=300,
                disabled=True,
                key=f"cover_output_{job_idx}"
            )
            st.download_button(
                "⬇️ Download Cover Letter",
                cover_letter,
                file_name=f"cover_letter_{job_idx}.txt",
                mime="text/plain",
                key=f"download_cover_{job_idx}"
            )
        else:
            st.error("Cover letter generation returned no content.")
    
    except requests.exceptions.Timeout:
        st.error(f"Cover letter generation timed out (>{API_TIMEOUT}s). Please try again.")
        logger.error("Cover letter generation timeout")
    except requests.exceptions.RequestException as e:
        st.error(f"Cover letter generation failed: {str(e)}")
        logger.error(f"Cover letter generation error: {e}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        logger.error(f"Unexpected error in cover letter generation: {e}")


# ============================================================================
# Sidebar Configuration
# ============================================================================

def render_sidebar():
    """Render sidebar with settings and information."""
    with st.sidebar:
        st.header("⚙️ Settings")
        
        st.info(
            "💡 **Tips:**\n"
            "- Upload your resume to calculate match scores and generate documents\n"
            "- Matches are based on visa signals and relevance\n"
            "- Generated documents are tailored to each job\n"
            "- Download all documents for your records"
        )
        
        st.divider()
        
        st.subheader("📊 Backend Configuration")
        st.code(f"Backend: {BACKEND_URL}", language="text")
        st.code(f"Timeout: {API_TIMEOUT}s", language="text")
        st.code(f"Max Retries: {MAX_RETRIES}", language="text")
        
        st.divider()
        
        if st.button("🔄 Clear Session"):
            st.session_state.clear()
            st.success("Session cleared.")


# ============================================================================
# Main Application
# ============================================================================

def main():
    """Main application entry point."""
    try:
        render_header()
        render_sidebar()
        
        st.divider()
        
        # Resume upload
        render_resume_uploader()
        
        st.divider()
        
        # Search form
        role, location, visa_type = render_search_form()
        
        # Search button
        if st.button("🚀 Search Jobs", type="primary", use_container_width=True):
            # Validate inputs
            is_valid, error_msg = validate_job_search_inputs(role, location, visa_type)
            if not is_valid:
                st.error(f"Input validation failed: {error_msg}")
            else:
                try:
                    with st.spinner("🔍 Searching for jobs..."):
                        result = search_jobs(
                            role=role,
                            location=location,
                            visa_type=visa_type,
                            resume_text=st.session_state.get("resume_text")
                        )
                    
                    if "jobs" in result:
                        st.session_state["jobs"] = result["jobs"]
                        st.session_state["filtered_out_jobs"] = result.get("filtered_out_jobs", 0)
                        st.session_state["total_scanned_jobs"] = result.get("total_scanned_jobs", len(result["jobs"]))
                        st.session_state["search_timestamp"] = time.time()
                        logger.info(f"Found {len(result['jobs'])} jobs")
                    else:
                        st.error("Search returned unexpected format.")
                        logger.error(f"Unexpected response format: {result}")
                
                except requests.exceptions.Timeout:
                    st.error(f"Search timed out after {API_TIMEOUT}s. Please try again.")
                    logger.error("Job search timeout")
                except requests.exceptions.RequestException as e:
                    st.error(f"Search failed: {str(e)}")
                    logger.error(f"Job search error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                    logger.error(f"Unexpected error in job search: {e}")
        
        st.divider()
        
        # Display results
        if "jobs" in st.session_state:
            render_job_results(st.session_state["jobs"])
    
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()
