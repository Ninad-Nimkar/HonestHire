import React, { useState, useRef } from 'react';

/**
 * JD Upload component — paste or upload job description.
 */
export default function JDUpload({ onExtracted, loading }) {
  const [text, setText] = useState('');
  const [fileName, setFileName] = useState('');
  const fileRef = useRef(null);

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (ev) => {
      setText(ev.target.result);
    };
    reader.readAsText(file);
  };

  const handleSubmit = () => {
    if (text.trim().length < 10) return;
    onExtracted(text.trim());
  };

  return (
    <div className="glass-card p-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
             style={{ background: 'rgba(124, 58, 237, 0.15)' }}>
          📋
        </div>
        <div>
          <h2 className="text-lg font-bold">Job Description</h2>
          <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            Paste or upload the job description to extract required skills
          </p>
        </div>
      </div>

      {/* Textarea */}
      <textarea
        className="textarea-field mb-4"
        rows={12}
        placeholder="Paste the full job description here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      {/* File upload row */}
      <div className="flex items-center gap-3 mb-5">
        <button
          onClick={() => fileRef.current?.click()}
          className="btn-secondary flex items-center gap-2"
        >
          <span>📎</span>
          <span>Upload .txt / .pdf</span>
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".txt,.pdf"
          onChange={handleFileUpload}
          className="hidden"
        />
        {fileName && (
          <span className="text-xs text-emerald-400 flex items-center gap-1.5">
            <span>✓</span> {fileName}
          </span>
        )}
      </div>

      {/* Character count */}
      <div className="flex items-center justify-between">
        <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
          {text.length > 0 ? `${text.length.toLocaleString()} characters` : 'No content yet'}
        </span>

        <button
          onClick={handleSubmit}
          disabled={text.trim().length < 10 || loading}
          className="btn-primary flex items-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin-slow inline-block">⟳</span>
              <span>Extracting...</span>
            </>
          ) : (
            <>
              <span>🔍</span>
              <span>Extract Skills</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
