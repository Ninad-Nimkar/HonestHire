import React from 'react';

/**
 * Individual skill card with tier selector buttons.
 */
export default function SkillCard({ skill, onTierChange, index }) {
  const tiers = [
    { key: 'blocker', label: 'BLOCKER' },
    { key: 'important', label: 'IMPORTANT' },
    { key: 'nice_to_have', label: 'NICE TO HAVE' },
  ];

  return (
    <div className="glass-card p-5 animate-fade-in"
         style={{ animationDelay: `${index * 0.05}s` }}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-base font-bold">{skill.name}</h3>
          {skill.aliases && skill.aliases.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {skill.aliases.map((alias, i) => (
                <span key={i}
                      className="text-[10px] px-2 py-0.5 rounded-full"
                      style={{
                        background: 'var(--color-bg-glass)',
                        color: 'var(--color-text-muted)',
                        border: '1px solid var(--color-border)',
                      }}>
                  {alias}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Flagged warning */}
      {skill.flagged_reason && (
        <div className="rounded-lg px-3 py-2 mb-3 flex items-start gap-2"
             style={{
               background: 'rgba(245, 158, 11, 0.08)',
               border: '1px solid rgba(245, 158, 11, 0.2)',
             }}>
          <span className="text-amber-400 text-sm mt-0.5">⚠️</span>
          <p className="text-xs text-amber-300/80 leading-relaxed">
            {skill.flagged_reason}
          </p>
        </div>
      )}

      {/* Tier buttons */}
      <div className="flex gap-2">
        {tiers.map((tier) => (
          <button
            key={tier.key}
            onClick={() => onTierChange(skill.name, tier.key)}
            className={`tier-btn ${tier.key} ${skill.tier === tier.key ? 'active' : ''} flex-1`}
          >
            {tier.label}
          </button>
        ))}
      </div>
    </div>
  );
}
