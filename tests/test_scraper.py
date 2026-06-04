from tools.seek_scraper import search_seek


jobs = search_seek(
    role="AI Engineer",
    location="All Adelaide SA"
)

print(f"\nJobs Found: {len(jobs)}\n")

for job in jobs[:3]:

    print("=" * 60)

    print("TITLE:")
    print(job["title"])

    print("\nCOMPANY:")
    print(job["company"])

    print("\nLOCATION:")
    print(job["location"])

    print("\nURL:")
    print(job["url"])

    print("\n")