import requests
import json

payload = {
    "task": {
        "input": {
            "job_description": "Software engineer position requiring 5+ years Python experience, available for visa sponsorship",
            "visa_type": "485"
        }
    }
}

r = requests.post('http://127.0.0.1:9004/invoke', json=payload)
print(json.dumps(r.json(), indent=2))
