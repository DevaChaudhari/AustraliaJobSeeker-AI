import { FormEvent, useState } from "react";
import { LOCATION_OPTIONS, MAX_FIELD_LENGTH, VISA_TYPE_OPTIONS } from "../constants";
import type { SearchParams } from "../types";
import { BriefcaseIcon, PinIcon, SearchIcon, ShieldIcon } from "./Icons";

interface Props {
  loading: boolean;
  onSearch: (params: Omit<SearchParams, "resume_text">) => void;
}

export function SearchForm({ loading, onSearch }: Props) {
  const [role, setRole] = useState("AI Engineer");
  const [location, setLocation] = useState(LOCATION_OPTIONS[0]);
  const [visaType, setVisaType] = useState("485");

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    onSearch({ role: role.trim(), location, visa_type: visaType });
  };

  return (
    <form className="search-form" onSubmit={handleSubmit}>
      <label className="field">
        <span className="field-label">Job role</span>
        <span className="field-control">
          <BriefcaseIcon />
          <input
            value={role}
            onChange={(e) => setRole(e.target.value)}
            maxLength={MAX_FIELD_LENGTH}
            placeholder="e.g. Machine Learning Engineer"
            required
          />
        </span>
      </label>
      <label className="field">
        <span className="field-label">Location</span>
        <span className="field-control">
          <PinIcon />
          <select value={location} onChange={(e) => setLocation(e.target.value)}>
            {LOCATION_OPTIONS.map((option) => (
              <option key={option}>{option}</option>
            ))}
          </select>
        </span>
      </label>
      <label className="field">
        <span className="field-label">Your visa</span>
        <span className="field-control">
          <ShieldIcon />
          <select value={visaType} onChange={(e) => setVisaType(e.target.value)}>
            {Object.entries(VISA_TYPE_OPTIONS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </span>
      </label>
      <button className="btn btn-primary btn-lg search-submit" type="submit" disabled={loading || !role.trim()}>
        <SearchIcon />
        {loading ? "Searching…" : "Search jobs"}
      </button>
    </form>
  );
}
