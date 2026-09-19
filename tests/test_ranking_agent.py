from australiajobseeker.agents.ranking_agent import rank_jobs, remove_duplicates


def _job(title, company, description, eligible):
    return {
        "title": title,
        "company": company,
        "full_description": description,
        "visa_result": {"eligible": eligible},
    }


def test_remove_duplicates_ignores_case():
    jobs = [
        _job("AI Engineer", "Acme", "", True),
        _job("ai engineer", "ACME", "", True),
        _job("Data Analyst", "Acme", "", True),
    ]
    assert len(remove_duplicates(jobs)) == 2


def test_visa_eligible_jobs_rank_first():
    jobs = [
        _job("Restricted", "A", "python", False),
        _job("Eligible", "B", "python", True),
    ]
    ranked = rank_jobs(jobs, resume_text="python")
    assert [j["title"] for j in ranked] == ["Eligible", "Restricted"]


def test_no_resume_means_no_match_score():
    ranked = rank_jobs([_job("Eligible", "B", "python", True)], resume_text=None)
    assert ranked[0]["profile_result"]["match_score"] is None
