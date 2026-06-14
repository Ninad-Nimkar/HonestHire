import React from 'react';
import VerificationBadge from './VerificationBadge';
import ScoreBreakdown from './ScoreBreakdown';

/**
 * Candidate card — summary card per candidate in ranked order.
 */
export default function CandidateCard({ scorecard, onClick }) {
  const { candidate_name, scores, weighted_total, confidence, ai_risk_score,
          final_rank, challenger_flags, excluded, exclusion_reason } = scorecard;

  const scoreLevel = weighted_total >= 0.75 ? 'high' : weighted_total >= 0.5 ? 'mid' : 'low';

  const aiRiskLevel = ai_risk_score >= 0.7 ? 'High'
                    : ai_risk_score >= 0.4 ? 'Medium'
                    : 'Low';

  const aiRiskColor = ai_risk_score >= 0.7 ? 'text-rose-400'
                    : ai_risk_score >= 0.4 ? 'text-amber-400'
                    : 'text-emerald-400';

  const rankClass = final_rank === 1 ? 'rank-1'
                  : final_rank === 2 ? 'rank-2'
                  : final_rank === 3 ? 'rank-3'
                  : '';

  if (excluded) {
    return (
      <div className="glass-card p-5 opacity-50 cursor-not-allowed">
        <div className="flex items-center gap-4">
          <div className="rank-badge bg-gray-600">—</div>
          <div className="flex-1">
            <p className="font-semibold line-through">{candidate_name}</p>
            <p className="text-xs text-rose-400 mt-1">
              Excluded: {exclusion_reason || 'Failed blocker skill'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-5 cursor-pointer group"
         onClick={onClick}>
      <div className="flex items-start gap-4">
        {/* Rank */}
        <div className={`rank-badge ${rankClass}`}>
          #{final_rank}
        </div>

        {/* Main info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-base font-bold truncate">{candidate_name}</h3>
            <VerificationBadge confidence={confidence} aiRiskScore={ai_risk_score} />
          </div>

          {/* Score + AI risk row */}
          <div className="flex items-center gap-4 mb-3">
            <div className={`score-badge ${scoreLevel}`}>
              {(weighted_total * 100).toFixed(0)}
            </div>
            <div className="flex-1">
              <p className="text-xs mb-1" style={{ color: 'var(--color-text-muted)' }}>
                Overall Score
              </p>
              <div className="h-1.5 rounded-full overflow-hidden"
                   style={{ background: 'var(--color-bg-glass)' }}>
                <div className="h-full rounded-full transition-all duration-500"
                     style={{
                       width: `${weighted_total * 100}%`,
                       background: scoreLevel === 'high' ? '#10b981'
                                 : scoreLevel === 'mid' ? '#f59e0b' : '#f43f5e',
                     }} />
              </div>
            </div>
            <div className="text-right">
              <p className="text-[10px] uppercase tracking-wider"
                 style={{ color: 'var(--color-text-muted)' }}>
                AI Risk
              </p>
              <p className={`text-xs font-bold ${aiRiskColor}`}>
                {aiRiskLevel}
              </p>
            </div>
          </div>

          {/* Mini score bars */}
          <ScoreBreakdown scores={scores} compact={true} />

          {/* Challenger flags preview */}
          {challenger_flags && challenger_flags.length > 0 && (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-amber-400 text-xs">⚠</span>
              <span className="text-[11px] text-amber-300/70">
                {challenger_flags.length} flag{challenger_flags.length > 1 ? 's' : ''} raised
              </span>
            </div>
          )}
        </div>

        {/* Expand indicator */}
        <div className="text-gray-500 group-hover:text-purple-400 transition-colors mt-2">
          <span className="text-lg">→</span>
        </div>
      </div>
    </div>
  );
}
