import { useState } from "react";

interface Props {
  title: string;
  text: string;
  filename: string;
}

export function GeneratedDoc({ title, text, filename }: Props) {
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
    <div className="doc">
      <div className="row">
        <h4>{title}</h4>
        <div className="actions">
          <button type="button" onClick={copy}>
            {copied ? "Copied" : "Copy"}
          </button>
          <button type="button" onClick={download}>
            Download
          </button>
        </div>
      </div>
      <pre>{text}</pre>
    </div>
  );
}
