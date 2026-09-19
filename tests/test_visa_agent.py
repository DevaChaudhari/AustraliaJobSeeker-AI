import pytest

from australiajobseeker.agents.visa_agent import check_visa_eligibility


@pytest.mark.parametrize(
    "description",
    [
        "Must be an Australian citizen.",
        "Role requires a baseline clearance.",
        "Permanent resident only.",
    ],
)
def test_citizen_clearance_and_pr_only_roles_are_restricted_for_student_visa(description):
    result = check_visa_eligibility(description, "500")
    assert result["status"] == "restricted"
    assert result["eligible"] is False


def test_permanent_resident_role_is_eligible_for_pr():
    result = check_visa_eligibility("Permanent resident required.", "PR")
    assert result["status"] == "likely_eligible"
    assert result["eligible"] is True


def test_sponsorship_is_eligible_for_482():
    result = check_visa_eligibility("Visa sponsorship available for the right person.", "482")
    assert result["status"] == "likely_eligible"


def test_empty_description_is_unknown():
    result = check_visa_eligibility("", "485")
    assert result["status"] == "unknown"


def test_job_description_keyword_is_accepted():
    result = check_visa_eligibility(job_description="Australian citizens only", visa_type="485")
    assert result["status"] == "restricted"
