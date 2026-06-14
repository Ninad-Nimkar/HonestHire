import React from 'react';
import SkillCard from './SkillCard';

/**
 * HR Priority Gate — full skill tiering interface.
 */
export default function HRGateView({ skills, onTierChange, onConfirm, loading }) {
  const ratedCount = skills.filter(s => s.tier).length;
  const totalCount = skills.length;
  const allRated = ratedCount === totalCount && totalCount > 0;
  const progressPct = totalCount > 0 ? (ratedCount / totalCount) * 100 : 0;

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">Skill Priority Gate</h2>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
            Rate each skill's importance to the role. This directly affects candidate scoring.
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm font-semibold">
            <span className="text-purple-400">{ratedCount}</span>
            <span style={{ color: 'var(--color-text-muted)' }}> of {totalCount}</span>
            <span style={{ color: 'var(--color-text-muted)' }}> rated</span>
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="progress-bar mb-6">
        <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
      </div>

      {/* Skills grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6 stagger-children">
        {skills.map((skill, idx) => (
          <SkillCard
            key={skill.name}
            skill={skill}
            onTierChange={onTierChange}
            index={idx}
          />
        ))}
      </div>

      {/* Confirm button */}
      <div className="flex justify-end">
        <button
          onClick={onConfirm}
          disabled={!allRated || loading}
          className="btn-primary flex items-center gap-2 text-base px-8 py-3"
        >
          {loading ? (
            <>
              <span className="animate-spin-slow inline-block">⟳</span>
              <span>Starting Pipeline...</span>
            </>
          ) : (
            <>
              <span>🚀</span>
              <span>Confirm & Run Pipeline</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
