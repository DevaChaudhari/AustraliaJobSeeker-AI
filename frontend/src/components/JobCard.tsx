import { useState } from "react";
import { ApiError, generateCoverLetter, generateResume } from "../api";
import type { Job } from "../types";
import { GeneratedDoc } from "./GeneratedDoc";

interface Props {
  job: Job;
  resumeText: string;
}

type Generated = { loading: boolean; text?: string; error?: string };

function scoreClass(score: number) {
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
  return [state, start] as const;
}

export function JobCard({ job, resumeText }: Props) {
  const [showDescription, setShowDescription] = useState(false);
  const [resume, generateResumeDoc] = useGenerator(() => generateResume(job, resumeText.trim()));
  const [cover, generateCoverDoc] = useGenerator(() => generateCoverLetter(job, resumeText.trim()));

  const slug = `${job.company}-${job.title}`.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

  return (
    <article className="panel job">
      <div className="job-head">
        <div>
          <h3>{job.title}</h3>
          <p className="meta">
            {job.company} · {job.location}
          </p>
        </div>
        {job.score_available && job.score !== null && (
          <div className={`score ${scoreClass(job.score)}`} title="Resume match score">
            {Math.round(job.score)}%
          </div>
        )}
      </div>

      <div className="badges">
        <span className={`badge ${job.eligible ? "good" : "ok"}`}>{job.eligibility_label}</span>
      </div>
      {job.eligibility_reason && <p className="reason">{job.eligibility_reason}</p>}

      {(job.matched_skills.length > 0 || job.missing_skills.length > 0) && (
        <div className="skills">
          {job.matched_skills.map((skill) => (
            <span key={`m-${skill}`} className="chip match">
              {skill}
            </span>
          ))}
          {job.missing_skills.map((skill) => (
            <span key={`x-${skill}`} className="chip missing">
              {skill}
            </span>
          ))}
        </div>
      )}

      <div className="actions">
        <a className="button primary" href={job.url} target="_blank" rel="noopener noreferrer">
          View &amp; apply
        </a>
        <button type="button" onClick={generateResumeDoc} disabled={resume?.loading}>
          {resume?.loading ? "Tailoring…" : "Tailor resume"}
        </button>
        <button type="button" onClick={generateCoverDoc} disabled={cover?.loading}>
          {cover?.loading ? "Writing…" : "Cover letter"}
        </button>
        <button type="button" className="link" onClick={() => setShowDescription((v) => !v)}>
          {showDescription ? "Hide description" : "Show description"}
        </button>
      </div>

      {showDescription && <pre className="description">{job.description}</pre>}

      {resume?.error && <p className="field-error">{resume.error}</p>}
      {resume?.text && <GeneratedDoc title="Tailored resume" text={resume.text} filename={`resume-${slug}.txt`} />}

      {cover?.error && <p className="field-error">{cover.error}</p>}
      {cover?.text && (
        <GeneratedDoc title="Cover letter" text={cover.text} filename={`cover-letter-${slug}.txt`} />
      )}
    </article>
  );
}
