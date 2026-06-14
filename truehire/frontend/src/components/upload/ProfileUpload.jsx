import React, { useState, useRef } from 'react';

/**
 * Candidate profile upload — drag-drop CSV or JSON.
 */
export default function ProfileUpload({ onUploaded, loading }) {
  const [file, setFile] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [candidateCount, setCandidateCount] = useState(0);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    const validExtensions = ['.csv', '.json'];
    const ext = f.name.substring(f.name.lastIndexOf('.')).toLowerCase();
    if (!validExtensions.includes(ext)) {
      alert('Please upload a .csv or .json file');
      return;
    }
    setFile(f);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files?.[0]);
  };

  const handleSubmit = async () => {
    if (!file) return;
    const result = await onUploaded(file);
    if (result?.count) {
      setCandidateCount(result.count);
    }
  };

  return (
    <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: '0.1s' }}>
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg"
             style={{ background: 'rgba(6, 182, 212, 0.15)' }}>
          👥
        </div>
        <div>
          <h2 className="text-lg font-bold">Candidate Profiles</h2>
          <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
            Upload candidate data as CSV or JSON
          </p>
        </div>
      </div>

      {/* Drop zone */}
      <div
        className={`drop-zone mb-4 ${dragOver ? 'dragover' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.json"
          onChange={(e) => handleFile(e.target.files?.[0])}
          className="hidden"
        />

        {file ? (
          <div className="text-center">
            <div className="text-3xl mb-2">📁</div>
            <p className="text-sm font-semibold">{file.name}</p>
            <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
              {(file.size / 1024).toFixed(1)} KB
              {candidateCount > 0 && ` • ${candidateCount} candidates`}
            </p>
            <button
              onClick={(e) => { e.stopPropagation(); setFile(null); setCandidateCount(0); }}
              className="text-xs text-rose-400 mt-2 hover:text-rose-300 transition-colors"
            >
              Remove
            </button>
          </div>
        ) : (
          <div className="text-center">
            <div className="text-4xl mb-3 opacity-40">⬆️</div>
            <p className="text-sm font-medium mb-1">
              Drop file here or <span className="text-purple-400">browse</span>
            </p>
            <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
              Accepts .csv or .json files
            </p>
          </div>
        )}
      </div>

      {/* Format hints */}
      <div className="rounded-lg p-3 mb-4"
           style={{ background: 'var(--color-bg-glass)', border: '1px solid var(--color-border)' }}>
        <p className="text-xs font-semibold mb-2" style={{ color: 'var(--color-text-secondary)' }}>
          Expected format:
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-[10px] font-mono text-purple-400 mb-0.5">CSV</p>
            <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>
              id, name, email, raw_cv, skills, linkedin_url, github_url
            </p>
          </div>
          <div>
            <p className="text-[10px] font-mono text-cyan-400 mb-0.5">JSON</p>
            <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>
              Array of candidate objects with profile fields
            </p>
          </div>
        </div>
      </div>

      {/* Submit */}
      <div className="flex justify-end">
        <button
          onClick={handleSubmit}
          disabled={!file || loading}
          className="btn-primary flex items-center gap-2"
        >
          {loading ? (
            <>
              <span className="animate-spin-slow inline-block">⟳</span>
              <span>Uploading...</span>
            </>
          ) : (
            <>
              <span>📤</span>
              <span>Upload Candidates</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
