from agents.supervisor_graph import graph


result = graph.invoke(
    {
        "role": "AI Engineer",
        "location": "All Adelaide SA",
        "visa_type": "500",
        "jobs": []
    }
)

print("\nTOTAL JOBS:")
print(len(result["jobs"]))

print("\nFIRST JOB:")
print(result["jobs"][0]["title"])

print("\nVISA RESULT:")
print(
    result["jobs"][0]["visa_result"]
)