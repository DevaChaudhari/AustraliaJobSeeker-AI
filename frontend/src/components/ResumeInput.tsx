import { ChangeEvent, DragEvent, useState } from "react";
import { MAX_RESUME_LENGTH } from "../constants";
import { extractResumeText } from "../resumeFile";
import { CheckIcon, FileIcon, UploadIcon } from "./Icons";

interface Props {
  value: string;
  onChange: (text: string) => void;
}

export function ResumeInput({ value, onChange }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [reading, setReading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const readFile = async (file: File) => {
    setError(null);
    setReading(true);
    try {
      const text = (await extractResumeText(file)).trim();
      if (!text) throw new Error("No readable text found in that file.");
      onChange(text.slice(0, MAX_RESUME_LENGTH));
      setFileName(file.name);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not read that file.");
    } finally {
      setReading(false);
    }
  };

  const handleFile = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (file) void readFile(file);
  };

  const handleDrop = (e: DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void readFile(file);
  };

  const clear = () => {
    onChange("");
    setFileName(null);
  };

  return (
    <div className="resume-input">
      <div className="card-head">
        <span className="card-icon">
          <FileIcon />
        </span>
        <div>
          <h2>Your resume</h2>
          <p className="muted small">Optional. Unlocks match scores and tailored documents.</p>
        </div>
      </div>

      <label
        className={`dropzone${dragging ? " is-dragging" : ""}${reading ? " is-busy" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <input type="file" accept=".pdf,.docx,.txt" onChange={handleFile} disabled={reading} hidden />
        <UploadIcon size={20} />
        <span className="dropzone-title">{reading ? "Reading file…" : "Upload or drop a file"}</span>
        <span className="muted small">PDF, DOCX or TXT</span>
      </label>

      {fileName && value && !error && (
        <p className="file-ok small">
          <CheckIcon size={14} /> Loaded {fileName}
        </p>
      )}
      {error && <p className="field-error">{error}</p>}

      <div className="divider-text">
        <span>or paste text</span>
      </div>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value.slice(0, MAX_RESUME_LENGTH))}
        rows={10}
        placeholder="Paste your resume here…"
        aria-label="Resume text"
      />
      <div className="row small muted">
        <span>{value.length.toLocaleString()} characters</span>
        {value && (
          <button type="button" className="btn-link" onClick={clear}>
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
