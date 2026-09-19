import type { Job, SearchParams, SearchResult } from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const POLL_INTERVAL_MS = 3000;
const SEARCH_TIMEOUT_MS = 10 * 60 * 1000;

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch {
    throw new ApiError("Could not reach the server. Check your connection and try again.");
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      // Non-JSON error body (e.g. a gateway timeout page); keep the generic message.
    }
    throw new ApiError(detail);
  }
  return response.json() as Promise<T>;
}

const post = <T>(path: string, body: unknown, signal?: AbortSignal) =>
  request<T>(path, { method: "POST", body: JSON.stringify(body), signal });

const sleep = (ms: number, signal?: AbortSignal) =>
  new Promise<void>((resolve, reject) => {
    const timer = setTimeout(resolve, ms);
    signal?.addEventListener("abort", () => {
      clearTimeout(timer);
      reject(new DOMException("Aborted", "AbortError"));
    });
  });

interface SearchStatus {
  status: "running" | "done" | "error";
  result?: SearchResult;
  error?: string;
}

/** Starts a search and polls until it finishes, so long scrapes don't hit gateway timeouts. */
export async function searchJobs(params: SearchParams, signal?: AbortSignal): Promise<SearchResult> {
  const { job_id } = await post<{ job_id: string }>("/search-jobs/async", params, signal);
  const deadline = Date.now() + SEARCH_TIMEOUT_MS;

  while (Date.now() < deadline) {
    await sleep(POLL_INTERVAL_MS, signal);
    const status = await request<SearchStatus>(`/search-jobs/${job_id}`, { signal });
    if (status.status === "done" && status.result) return status.result;
    if (status.status === "error") throw new ApiError(status.error ?? "Search failed");
  }
  throw new ApiError("The search took too long. Please try again.");
}

export async function generateResume(job: Job, resumeText: string): Promise<string> {
  const { resume } = await post<{ resume: string }>("/generate-resume", {
    resume_text: resumeText || undefined,
    job_description: job.description,
  });
  return resume;
}

export async function generateCoverLetter(job: Job, resumeText: string): Promise<string> {
  const { cover_letter } = await post<{ cover_letter: string }>("/generate-cover-letter", {
    resume_text: resumeText || undefined,
    job_description: job.description,
    company: job.company,
    title: job.title,
  });
  return cover_letter;
}
