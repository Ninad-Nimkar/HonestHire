import React from 'react';

/**
 * Verification badge — Verified / Flagged / Needs Review.
 */
export default function VerificationBadge({ confidence, aiRiskScore }) {
  let icon, label, colorClass, bgStyle;

  if (confidence === 'high' && aiRiskScore < 0.3) {
    icon = '✓';
    label = 'Verified';
    colorClass = 'text-emerald-400';
    bgStyle = { background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.25)' };
  } else if (confidence === 'needs_review' || aiRiskScore >= 0.7) {
    icon = '🔍';
    label = 'Needs Review';
    colorClass = 'text-amber-400';
    bgStyle = { background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.25)' };
  } else if (confidence === 'low' || aiRiskScore >= 0.5) {
    icon = '⚠';
    label = 'Flagged';
    colorClass = 'text-rose-400';
    bgStyle = { background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.25)' };
  } else {
    icon = '✓';
    label = 'Verified';
    colorClass = 'text-emerald-400';
    bgStyle = { background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.25)' };
  }

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${colorClass}`}
          style={bgStyle}>
      <span>{icon}</span>
      {label}
    </span>
  );
}
