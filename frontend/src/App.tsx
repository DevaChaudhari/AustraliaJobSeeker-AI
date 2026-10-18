import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ApiError, searchJobs } from "./api";
import { AlertIcon, BriefcaseIcon, FileIcon, SearchIcon, ShieldIcon, SparkIcon } from "./components/Icons";
import { JobCard } from "./components/JobCard";
import { ResumeInput } from "./components/ResumeInput";
import { SearchForm } from "./components/SearchForm";
import type { SearchParams, SearchResult } from "./types";

type SortOrder = "relevance" | "score";

function useElapsedSeconds(active: boolean) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!active) return;
    setSeconds(0);
    const timer = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(timer);
  }, [active]);
  return seconds;
}

function SkeletonCard() {
  return (
    <div className="card job skeleton" aria-hidden="true">
      <div className="job-head">
        <div className="sk sk-avatar" />
        <div className="job-title-block">
          <div className="sk sk-line w60" />
          <div className="sk sk-line w35" />
        </div>
      </div>
      <div className="sk sk-pill" />
      <div className="sk sk-line w90" />
      <div className="sk sk-line w70" />
    </div>
  );
}

const FEATURES = [
  { icon: SearchIcon, title: "Live listings", text: "Fresh roles pulled from Seek on every search." },
  { icon: ShieldIcon, title: "Visa-aware", text: "Each ad checked for your visa's work rights." },
  { icon: SparkIcon, title: "AI documents", text: "Tailored resume and cover letter in seconds." },
];

export default function App() {
  const [resumeText, setResumeText] = useState("");
  const [result, setResult] = useState<SearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sortOrder, setSortOrder] = useState<SortOrder>("relevance");
  const abortRef = useRef<AbortController | null>(null);
  const resultsRef = useRef<HTMLDivElement | null>(null);
  const elapsed = useElapsedSeconds(loading);

  const handleSearch = useCallback(
    async (params: Omit<SearchParams, "resume_text">) => {
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setLoading(true);
      setError(null);
      setResult(null);
      setSortOrder("relevance");
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
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

  const jobs = useMemo(() => {
    if (!result) return [];
    if (sortOrder === "score" && result.score_available) {
      return [...result.jobs].sort((a, b) => (b.score ?? -1) - (a.score ?? -1));
    }
    return result.jobs;
  }, [result, sortOrder]);

  return (
    <div className="app">
      <header className="topbar">
        <div className="container topbar-inner">
          <a className="brand" href="/" aria-label="AustraliaJobSeeker AI home">
            <span className="brand-mark">
              <BriefcaseIcon size={18} />
            </span>
            <span className="brand-name">
              AustraliaJobSeeker <span className="brand-accent">AI</span>
            </span>
          </a>
          <span className="topbar-tag">Visa-aware job search for Australia</span>
        </div>
      </header>

      <section className="hero">
        <div className="container">
          <span className="eyebrow">For international students &amp; graduates</span>
          <h1>Find jobs in Australia you're actually allowed to take.</h1>
          <p className="hero-sub">
            Search live listings, see which roles fit your visa, and generate a tailored resume and cover letter
            for any job, in one place.
          </p>
          <div className="card search-card">
            <SearchForm loading={loading} onSearch={handleSearch} />
          </div>
          <ul className="features">
            {FEATURES.map(({ icon: FeatureIcon, title, text }) => (
              <li key={title}>
                <span className="feature-icon">
                  <FeatureIcon size={18} />
                </span>
                <div>
                  <strong>{title}</strong>
                  <span>{text}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <main className="container layout" ref={resultsRef}>
        <aside className="card sidebar">
          <ResumeInput value={resumeText} onChange={setResumeText} />
        </aside>

        <section className="results" aria-live="polite">
          {!loading && !result && !error && (
            <div className="card empty-state">
              <span className="empty-icon">
                <SearchIcon size={26} />
              </span>
              <h2>Start a search</h2>
              <p className="muted">
                Choose a role, location and your visa above. Add your resume to see how well you
                match each job.
              </p>
            </div>
          )}

          {loading && (
            <>
              <div className="card status" role="status">
                <span className="spinner" aria-hidden="true" />
                <div>
                  <strong>Searching live listings and checking visa eligibility…</strong>
                  <span className="muted small">
                    This usually takes under a minute · {elapsed}s elapsed
                  </span>
                </div>
              </div>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          )}

          {error && (
            <div className="card alert" role="alert">
              <AlertIcon size={20} />
              <div>
                <strong>Search failed</strong>
                <span>{error}</span>
              </div>
            </div>
          )}

          {result && (
            <>
              <div className="results-toolbar">
                <div>
                  <h2 className="results-title">
                    {result.total_jobs} {result.total_jobs === 1 ? "job" : "jobs"} match your visa
                  </h2>
                  <p className="muted small">
                    {result.total_scanned_jobs} scanned
                    {result.filtered_out_jobs > 0 && ` · ${result.filtered_out_jobs} filtered out as restricted`}
                    {!result.score_available && " · add your resume to see match scores"}
                  </p>
                </div>
                {result.score_available && result.jobs.length > 1 && (
                  <label className="sort">
                    <span className="small muted">Sort by</span>
                    <select value={sortOrder} onChange={(e) => setSortOrder(e.target.value as SortOrder)}>
                      <option value="relevance">Relevance</option>
                      <option value="score">Best match</option>
                    </select>
                  </label>
                )}
              </div>

              {jobs.length === 0 && (
                <div className="card empty-state">
                  <span className="empty-icon">
                    <FileIcon size={26} />
                  </span>
                  <h2>No visa-suitable jobs found</h2>
                  <p className="muted">Try a broader role, a different city, or All Australia.</p>
                </div>
              )}

              {jobs.map((job) => (
                <JobCard key={job.url} job={job} resumeText={resumeText} />
              ))}
            </>
          )}
        </section>
      </main>

      <footer className="footer">
        <div className="container footer-inner">
          <span>© {new Date().getFullYear()} AustraliaJobSeeker AI</span>
          <span>
            Eligibility results are guidance only. Always confirm work rights with the employer and the
            Department of Home Affairs.
          </span>
        </div>
      </footer>
    </div>
  );
}
