import { useState } from "react";
import { CheckIcon, CloseIcon, CopyIcon, DownloadIcon } from "./Icons";

interface Props {
  title: string;
  text: string;
  filename: string;
  onClose: () => void;
}

export function GeneratedDoc({ title, text, filename, onClose }: Props) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // Clipboard can be unavailable (insecure context / denied permission); download still works.
    }
  };

  const download = () => {
    const url = URL.createObjectURL(new Blob([text], { type: "text/plain;charset=utf-8" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <section className="doc" aria-label={title}>
      <div className="doc-head">
        <h4>{title}</h4>
        <div className="doc-actions">
          <button type="button" className="btn btn-ghost btn-sm" onClick={copy}>
            {copied ? <CheckIcon size={15} /> : <CopyIcon size={15} />}
            {copied ? "Copied" : "Copy"}
          </button>
          <button type="button" className="btn btn-ghost btn-sm" onClick={download}>
            <DownloadIcon size={15} />
            Download
          </button>
          <button type="button" className="btn btn-icon btn-sm" onClick={onClose} aria-label={`Close ${title}`}>
            <CloseIcon size={15} />
          </button>
        </div>
      </div>
      <pre>{text}</pre>
    </section>
  );
}
