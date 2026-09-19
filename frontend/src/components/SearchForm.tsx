import { FormEvent, useState } from "react";
import { LOCATION_OPTIONS, MAX_FIELD_LENGTH, VISA_TYPE_OPTIONS } from "../constants";
import type { SearchParams } from "../types";

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
      <label>
        Job role
        <input
          value={role}
          onChange={(e) => setRole(e.target.value)}
          maxLength={MAX_FIELD_LENGTH}
          placeholder="e.g. Machine Learning Engineer"
          required
        />
      </label>
      <label>
        Location
        <select value={location} onChange={(e) => setLocation(e.target.value)}>
          {LOCATION_OPTIONS.map((option) => (
            <option key={option}>{option}</option>
          ))}
        </select>
      </label>
      <label>
        Visa type
        <select value={visaType} onChange={(e) => setVisaType(e.target.value)}>
          {Object.entries(VISA_TYPE_OPTIONS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </label>
      <button className="primary" type="submit" disabled={loading || !role.trim()}>
        {loading ? "Searching…" : "Search jobs"}
      </button>
    </form>
  );
}
