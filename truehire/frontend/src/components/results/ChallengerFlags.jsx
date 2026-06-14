import React from 'react';

/**
 * Challenger flags — list of LLM-B critique flags.
 */
export default function ChallengerFlags({ flags }) {
  if (!flags || flags.length === 0) return null;

  return (
    <div className="space-y-2">
      <h4 className="text-xs font-semibold uppercase tracking-wider text-amber-400">
        Challenger Flags ({flags.length})
      </h4>
      <div className="flex flex-wrap gap-2">
        {flags.map((flag, i) => (
          <span key={i}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs"
                style={{
                  background: 'rgba(245, 158, 11, 0.08)',
                  border: '1px solid rgba(245, 158, 11, 0.2)',
                  color: 'rgba(251, 191, 36, 0.9)',
                }}>
            <span>⚠</span>
            {flag}
          </span>
        ))}
      </div>
    </div>
  );
}
