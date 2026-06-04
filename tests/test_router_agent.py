from agents.router_agent import (
    route_query
)


queries = [

    "Find AI jobs in Adelaide",

    "Check visa eligibility for this role",

    "Tailor my resume for this job",

    "Rank these jobs"
]

for query in queries:

    print("\nQUERY:")
    print(query)

    print("\nROUTE:")

    print(
        route_query(query)
    )

    print("\n" + "=" * 50)