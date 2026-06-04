from pydantic import BaseModel

class Job(BaseModel):
    title: str
    company: str
    location: str
    description: str
    url: str