from agents.supervisor_agent import (
    search_node,
    enrich_node,
    visa_node
)

state = {
    "role": "AI Engineer",
    "location": "All Adelaide SA",
    "visa_type": "500",
    "jobs": []
}

state = search_node(state)

print(
    f"\nSearch Results: {len(state['jobs'])}"
)

state = enrich_node(state)

print(
    f"Enriched Jobs: {len(state['jobs'])}"
)

state = visa_node(state)

print("\nFIRST JOB:\n")

print(state["jobs"][0]["title"])

print("\nVISA RESULT:\n")

print(
    state["jobs"][0]["visa_result"]
)