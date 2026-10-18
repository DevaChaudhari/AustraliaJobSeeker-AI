import { useState, type CSSProperties } from "react";
import { ApiError, generateCoverLetter, generateResume } from "../api";
import type { Job } from "../types";
import { GeneratedDoc } from "./GeneratedDoc";
import { AlertIcon, ChevronIcon, ExternalIcon, FileIcon, PinIcon, ShieldIcon, SparkIcon } from "./Icons";

interface Props {
  job: Job;
  resumeText: string;
}

type Generated = { loading: boolean; text?: string; error?: string };

function scoreTone(score: number) {
  if (score >= 70) return "good";
  if (score >= 40) return "ok";
  return "low";
}

function useGenerator(run: () => Promise<string>) {
  const [state, setState] = useState<Generated | null>(null);

  const start = async () => {
    setState({ loading: true });
    try {
      setState({ loading: false, text: await run() });
    } catch (e) {
      setState({ loading: false, error: e instanceof ApiError ? e.message : "Generation failed. Please try again." });
    }
  };
  return [state, start, () => setState(null)] as const;
}

function ScoreRing({ score }: { score: number }) {
  const value = Math.max(0, Math.min(100, Math.round(score)));
  return (
    <div className={`score-ring ${scoreTone(value)}`} style={{ "--value": value } as CSSProperties}>
      <span className="score-value">{value}%</span>
      <span className="score-label">match</span>
    </div>
  );
}

export function JobCard({ job, resumeText }: Props) {
  const [showDescription, setShowDescription] = useState(false);
  const [resume, generateResumeDoc, closeResume] = useGenerator(() => generateResume(job, resumeText.trim()));
  const [cover, generateCoverDoc, closeCover] = useGenerator(() => generateCoverLetter(job, resumeText.trim()));

  const slug = `${job.company}-${job.title}`.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  const initial = (job.company || job.title || "?").trim().charAt(0).toUpperCase();

  return (
    <article className="card job">
      <div className="job-head">
        <div className="company-avatar" aria-hidden="true">
          {initial}
        </div>
        <div className="job-title-block">
          <h3>{job.title}</h3>
          <p className="job-meta">
            <span>{job.company}</span>
            <span className="dot" aria-hidden="true" />
            <span className="with-icon">
              <PinIcon size={14} />
              {job.location}
            </span>
          </p>
        </div>
        {job.score_available && job.score !== null && <ScoreRing score={job.score} />}
      </div>

      <div className="eligibility">
        <span className={`badge ${job.eligible ? "badge-good" : "badge-warn"}`}>
          <ShieldIcon size={14} />
          {job.eligibility_label}
        </span>
        {job.eligibility_reason && <p className="muted small">{job.eligibility_reason}</p>}
      </div>

      {(job.matched_skills.length > 0 || job.missing_skills.length > 0) && (
        <div className="skills">
          {job.matched_skills.length > 0 && (
            <div className="skill-group">
              <span className="skill-heading">Matched</span>
              <div className="chips">
                {job.matched_skills.map((skill) => (
                  <span key={`m-${skill}`} className="chip chip-match">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
          {job.missing_skills.length > 0 && (
            <div className="skill-group">
              <span className="skill-heading">To develop</span>
              <div className="chips">
                {job.missing_skills.map((skill) => (
                  <span key={`x-${skill}`} className="chip chip-missing">
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      <div className="job-actions">
        <a className="btn btn-primary" href={job.url} target="_blank" rel="noopener noreferrer">
          View &amp; apply
          <ExternalIcon size={15} />
        </a>
        <button type="button" className="btn btn-secondary" onClick={generateResumeDoc} disabled={resume?.loading}>
          {resume?.loading ? <span className="spinner spinner-sm" /> : <SparkIcon size={15} />}
          {resume?.loading ? "Tailoring…" : "Tailor resume"}
        </button>
        <button type="button" className="btn btn-secondary" onClick={generateCoverDoc} disabled={cover?.loading}>
          {cover?.loading ? <span className="spinner spinner-sm" /> : <FileIcon size={15} />}
          {cover?.loading ? "Writing…" : "Cover letter"}
        </button>
        <button
          type="button"
          className="btn-link toggle"
          aria-expanded={showDescription}
          onClick={() => setShowDescription((v) => !v)}
        >
          {showDescription ? "Hide description" : "Job description"}
          <ChevronIcon size={15} className={showDescription ? "rotated" : undefined} />
        </button>
      </div>

      {showDescription && <pre className="description">{job.description}</pre>}

      {resume?.error && (
        <p className="inline-error">
          <AlertIcon size={15} /> {resume.error}
        </p>
      )}
      {resume?.text && (
        <GeneratedDoc
          title="Tailored resume"
          text={resume.text}
          filename={`resume-${slug}.txt`}
          onClose={closeResume}
        />
      )}

      {cover?.error && (
        <p className="inline-error">
          <AlertIcon size={15} /> {cover.error}
        </p>
      )}
      {cover?.text && (
        <GeneratedDoc
          title="Cover letter"
          text={cover.text}
          filename={`cover-letter-${slug}.txt`}
          onClose={closeCover}
        />
      )}
    </article>
  );
}
