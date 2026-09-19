import { ChangeEvent, useState } from "react";
import { MAX_RESUME_LENGTH } from "../constants";
import { extractResumeText } from "../resumeFile";

interface Props {
  value: string;
  onChange: (text: string) => void;
}

export function ResumeInput({ value, onChange }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [reading, setReading] = useState(false);

  const handleFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;

    setError(null);
    setReading(true);
    try {
      const text = (await extractResumeText(file)).trim();
      if (!text) throw new Error("No readable text found in that file.");
      onChange(text.slice(0, MAX_RESUME_LENGTH));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not read that file.");
    } finally {
      setReading(false);
    }
  };

  return (
    <div className="resume-input">
      <h2>Your resume</h2>
      <p className="hint">Optional. Adds match scores and is used to tailor your resume and cover letter.</p>
      <label className="file-button">
        {reading ? "Reading…" : "Upload .pdf, .docx or .txt"}
        <input type="file" accept=".pdf,.docx,.txt" onChange={handleFile} disabled={reading} hidden />
      </label>
      {error && <p className="field-error">{error}</p>}
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_RESUME_LENGTH))}
        rows={14}
        placeholder="…or paste your resume text here"
      />
      <div className="hint row">
        <span>{value.length.toLocaleString()} characters</span>
        {value && (
          <button type="button" className="link" onClick={() => onChange("")}>
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
