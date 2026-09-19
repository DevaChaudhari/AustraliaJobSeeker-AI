import { useCallback, useRef, useState } from "react";
import { ApiError, searchJobs } from "./api";
import { JobCard } from "./components/JobCard";
import { ResumeInput } from "./components/ResumeInput";
import { SearchForm } from "./components/SearchForm";
import type { SearchParams, SearchResult } from "./types";

export default function App() {
  const [resumeText, setResumeText] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const handleSearch = useCallback(
    async (params: Omit<SearchParams, "resume_text">) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setLoading(true);
      setError(null);
      setResult(null);
      try {
        setResult(
          await searchJobs({ ...params, resume_text: resumeText.trim() || undefined }, controller.signal),
        );
      } catch (e) {
        if (e instanceof DOMException && e.name === "AbortError") return;
        setError(e instanceof ApiError ? e.message : "Something went wrong. Please try again.");
      } finally {
        if (abortRef.current === controller) setLoading(false);
      }
    },
    [resumeText],
  );

  return (
    <div className="page">
      <header className="hero">
        <h1>AustraliaJobSeeker AI</h1>
        <p>
          Find visa-friendly jobs in Australia, see how well you match, and generate a tailored resume and
          cover letter in one click.
        </p>
      </header>

      <main className="layout">
        <aside className="panel side">
          <ResumeInput value={resumeText} onChange={setResumeText} />
        </aside>

        <section className="main">
          <div className="panel">
            <SearchForm loading={loading} onSearch={handleSearch} />
          </div>

          {loading && (
            <div className="panel status" role="status">
              <span className="spinner" aria-hidden="true" />
              Searching and checking visa eligibility… this usually takes a minute or two.
            </div>
          )}

          {error && (
            <div className="panel error" role="alert">
              {error}
            </div>
          )}

          {result && (
            <>
              <p className="summary">
                Showing <strong>{result.total_jobs}</strong> visa-suitable jobs from{" "}
                <strong>{result.total_scanned_jobs}</strong> scanned
                {result.filtered_out_jobs > 0 && ` (${result.filtered_out_jobs} filtered out)`}.
                {!result.score_available && " Add your resume to see match scores."}
              </p>
              {result.jobs.length === 0 && (
                <div className="panel">No visa-suitable jobs found. Try a different role or location.</div>
              )}
              {result.jobs.map((job) => (
                <JobCard key={job.url} job={job} resumeText={resumeText} />
              ))}
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        Eligibility results are guidance only — always confirm details with the employer and the Department
        of Home Affairs.
      </footer>
    </div>
  );
}
