import type { Job, SearchParams, SearchResult } from "./types";

const BASE_URL = (import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

const SEARCH_TIMEOUT_MS = 10 * 60 * 1000;

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (error) {
    // Let cancellations and timeouts through so callers can tell them apart from network errors.
    if (error instanceof DOMException && (error.name === "AbortError" || error.name === "TimeoutError")) {
      throw error;
    }
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

/**
 * Runs a search in one request. The backend (an AWS Lambda Function URL) can hold a request open
 * for up to 15 minutes, and Lambda keeps no memory between calls, so start-then-poll would not work.
 */
export async function searchJobs(params: SearchParams, signal?: AbortSignal): Promise<SearchResult> {
  const timeout = AbortSignal.timeout(SEARCH_TIMEOUT_MS);
  const combined = signal ? AbortSignal.any([signal, timeout]) : timeout;
  try {
    return await post<SearchResult>("/search-jobs", params, combined);
  } catch (error) {
    if (timeout.aborted && !signal?.aborted) {
      throw new ApiError("The search took too long. Please try again.");
    }
    throw error;
  }
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
