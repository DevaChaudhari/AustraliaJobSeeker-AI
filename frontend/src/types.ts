export interface SearchParams {
  role: string;
  location: string;
  visa_type: string;
  resume_text?: string;
}

export interface Job {
  title: string;
  company: string;
  location: string;
  score: number | null;
  score_available: boolean;
  matched_skills: string[];
  missing_skills: string[];
  eligible: boolean;
  eligibility_status: string;
  eligibility_label: string;
  eligibility_reasons: string[];
  eligibility_reason: string;
  eligibility_source: string;
  url: string;
  description: string;
}

export interface SearchResult {
  total_jobs: number;
  total_scanned_jobs: number;
  filtered_out_jobs: number;
  score_available: boolean;
  jobs: Job[];
}
