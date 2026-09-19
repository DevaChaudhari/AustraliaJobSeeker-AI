from australiajobseeker.agents.profile_agent import calculate_match_score, extract_skills


def test_extract_skills_is_case_insensitive():
    skills = extract_skills("Built APIs with Python and FastAPI on Docker")
    assert {"python", "fastapi", "docker"} <= set(skills)


def test_match_score_reports_matched_and_missing_skills():
    result = calculate_match_score(
        resume_text="Python and Docker",
        job_description="Python, Docker and AWS required",
    )
    assert set(result["matched_skills"]) == {"python", "docker"}
    assert result["missing_skills"] == ["aws"]
    assert result["match_score"] == 66


def test_match_score_is_zero_when_job_lists_no_known_skills():
    result = calculate_match_score("Python", "Friendly team, great coffee")
    assert result["match_score"] == 0
