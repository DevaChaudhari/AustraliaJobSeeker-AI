STATUS_LABELS = {
    "likely_eligible": "Likely eligible",
    "restricted": "Restricted",
    "unknown": "Unknown",
}

RISK_LEVELS = {
    "likely_eligible": "LOW",
    "restricted": "HIGH",
    "unknown": "UNKNOWN",
}


def _as_reason_list(value):
    if not value:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def _build_result(status, reasons, source, citations=None, raw_output=None):
    result = {
        "eligible": status == "likely_eligible",
        "status": status,
        "label": STATUS_LABELS[status],
        "score": 100 if status == "likely_eligible" else 0,
        "risk_level": RISK_LEVELS[status],
        "reasons": _as_reason_list(reasons),
        "source": source,
    }

    if citations is not None:
        result["citations"] = citations
    if raw_output is not None:
        result["raw_output"] = raw_output

    return result


def _normalise_text(text):
    return " ".join((text or "").lower().split())


def _find_terms(text, terms):
    found = []
    for term in sorted(terms, key=len, reverse=True):
        if term in text and not any(term in existing for existing in found):
            found.append(term)
    return found


def _format_terms(terms):
    shown_terms = terms[:3]
    return ", ".join(f"'{term}'" for term in shown_terms)


def _detect_job_ad_signal(full_description: str, visa_type: str):
    text = _normalise_text(full_description)
    selected_visa = str(visa_type or "").upper()

    if not text:
        return _build_result(
            "unknown",
            ["No job description was available to check visa requirements."],
            "job_ad",
        )

    citizen_terms = [
        "australian citizen",
        "australian citizens only",
        "citizen only",
        "citizens only",
        "citizenship required",
        "must be a citizen",
        "must be an australian citizen",
        "australian citizenship",
    ]
    permanent_resident_terms = [
        "permanent resident only",
        "permanent residents only",
        "permanent resident required",
        "permanent residency required",
        "pr required",
        "australian citizen or permanent resident",
        "citizen or permanent resident",
    ]
    clearance_terms = [
        "security clearance",
        "baseline clearance",
        "nv1 clearance",
        "nv2 clearance",
        "negative vetting",
    ]
    full_work_rights_terms = [
        "full working rights",
        "full work rights",
        "unrestricted working rights",
        "unrestricted work rights",
        "unrestricted right to work",
    ]
    right_to_work_terms = [
        "right to work in australia",
        "valid work rights",
        "valid working rights",
        "working rights in australia",
    ]
    sponsorship_terms = [
        "visa sponsorship available",
        "sponsorship available",
        "482 sponsorship",
        "tss sponsorship",
        "temporary skill shortage",
        "open to sponsorship",
        "will sponsor",
        "sponsor eligible candidates",
    ]
    student_terms = [
        "student visa",
        "subclass 500",
        "visa 500",
        "48 hours per fortnight",
    ]
    graduate_terms = [
        "graduate visa",
        "temporary graduate visa",
        "subclass 485",
        "visa 485",
    ]
    full_time_terms = [
        "full time",
        "full-time",
    ]

    found = _find_terms(text, citizen_terms)
    if found:
        return _build_result(
            "restricted",
            [f"Job ad mentions {_format_terms(found)}, which usually requires Australian citizenship."],
            "job_ad",
        )

    found = _find_terms(text, clearance_terms)
    if found:
        return _build_result(
            "restricted",
            [f"Job ad mentions {_format_terms(found)}, which may require Australian citizenship or clearance."],
            "job_ad",
        )

    found = _find_terms(text, permanent_resident_terms)
    if found and selected_visa != "PR":
        return _build_result(
            "restricted",
            [f"Job ad mentions {_format_terms(found)}, which does not match the selected visa type."],
            "job_ad",
        )
    if found and selected_visa == "PR":
        return _build_result(
            "likely_eligible",
            [f"Job ad mentions {_format_terms(found)}, which matches permanent resident work rights."],
            "job_ad",
        )

    found = _find_terms(text, full_work_rights_terms)
    if found and selected_visa in {"500", "482"}:
        return _build_result(
            "restricted",
            [f"Job ad asks for {_format_terms(found)}; this may not match the selected visa type."],
            "job_ad",
        )
    if found and selected_visa in {"485", "PR"}:
        return _build_result(
            "likely_eligible",
            [f"Job ad asks for {_format_terms(found)}, which usually matches this visa's work rights."],
            "job_ad",
        )

    found = _find_terms(text, right_to_work_terms)
    if found and selected_visa in {"485", "PR"}:
        return _build_result(
            "likely_eligible",
            [f"Job ad asks for {_format_terms(found)}, which usually matches this visa's work rights."],
            "job_ad",
        )

    if selected_visa == "500" and _find_terms(text, full_time_terms):
        return _build_result(
            "restricted",
            ["Job ad appears to be full-time; Student Visa 500 has work-hour limits during study periods."],
            "job_ad",
        )

    found = _find_terms(text, sponsorship_terms)
    if found and selected_visa == "482":
        return _build_result(
            "likely_eligible",
            [f"Job ad mentions {_format_terms(found)}, which is relevant to 482 sponsorship."],
            "job_ad",
        )
    if found:
        return _build_result(
            "unknown",
            [f"Job ad mentions {_format_terms(found)}, but not eligibility for the selected visa type."],
            "job_ad",
        )

    found = _find_terms(text, student_terms)
    if found and selected_visa == "500":
        return _build_result(
            "likely_eligible",
            [f"Job ad mentions {_format_terms(found)}, which is relevant to Student Visa 500."],
            "job_ad",
        )

    found = _find_terms(text, graduate_terms)
    if found and selected_visa == "485":
        return _build_result(
            "likely_eligible",
            [f"Job ad mentions {_format_terms(found)}, which is relevant to Temporary Graduate Visa 485."],
            "job_ad",
        )

    if selected_visa in {"485", "PR"}:
        return _build_result(
            "likely_eligible",
            ["No citizen-only, clearance, or permanent-resident restriction was found in the job ad."],
            "job_ad",
        )

    return None


def _mentions_visa_context(full_description: str):
    text = _normalise_text(full_description)
    context_terms = [
        "visa",
        "sponsor",
        "sponsorship",
        "work rights",
        "working rights",
        "right to work",
        "citizen",
        "permanent resident",
        "security clearance",
        "clearance",
    ]
    return bool(_find_terms(text, context_terms))


def _fallback_visa_result(full_description: str, visa_type: str):
    text = _normalise_text(full_description)

    blocked_terms = [
        "australian citizen",
        "citizenship required",
        "must be a citizen",
        "permanent resident only",
        "pr required",
        "security clearance",
        "baseline clearance",
        "nv1 clearance",
        "full working rights",
    ]

    found_terms = [term for term in blocked_terms if term in text]

    if found_terms:
        return _build_result("restricted", found_terms, "fallback")

    return _build_result(
        "unknown",
        ["No visa or sponsorship requirements were found in the job ad."],
        "fallback",
    )


def check_visa_eligibility(
    full_description: str = "",
    visa_type: str = "",
    job_description: str = "",
):
    if job_description and not full_description:
        full_description = job_description

    ad_signal = _detect_job_ad_signal(full_description, visa_type)
    if ad_signal:
        return ad_signal

    if not _mentions_visa_context(full_description):
        return _build_result(
            "unknown",
            ["No visa or sponsorship requirements were found in the job ad."],
            "job_ad",
        )

    return _build_result(
        "unknown",
        ["The job ad mentions visa/work-rights terms, but does not clearly confirm eligibility for the selected visa."],
        "job_ad",
    )
