from typing import TypedDict


class JobState(TypedDict):

    role: str

    location: str

    visa_type: str

    jobs: list

    ranked_jobs: list