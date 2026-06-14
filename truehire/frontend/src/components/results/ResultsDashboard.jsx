import React, { useState } from 'react';
import CandidateCard from './CandidateCard';
import ScoreBreakdown from './ScoreBreakdown';
import ChallengerFlags from './ChallengerFlags';
import VerificationBadge from './VerificationBadge';

/**
 * Results Dashboard — full ranked results view with filters and scorecard drawer.
 */
export default function ResultsDashboard({ results, onDownloadCSV }) {
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [filterConfidence, setFilterConfidence] = useState('all');
  const [sortBy, setSortBy] = useState('rank');
  const [drawerOpen, setDrawerOpen] = useState(false);

  if (!results || !results.scorecards) {
    return (
      <div className="flex items-center justify-center h-64">
        <p style={{ color: 'var(--color-text-muted)' }}>No results available</p>
      </div>
    );
  }

  // Filter
  let filtered = [...results.scorecards];
  if (filterConfidence !== 'all') {
    filtered = filtered.filter(s => s.confidence === filterConfidence);
  }

  // Sort
  if (sortBy === 'score') {
    filtered.sort((a, b) => b.weighted_total - a.weighted_total);
  } else if (sortBy === 'name') {
    filtered.sort((a, b) => a.candidate_name.localeCompare(b.candidate_name));
  } else {
    filtered.sort((a, b) => a.final_rank - b.final_rank);
  }

  const openDrawer = (sc) => {
    setSelectedCandidate(sc);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setTimeout(() => setSelectedCandidate(null), 300);
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">{results.job_title || 'Results'}</h2>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-secondary)' }}>
            {results.total_candidates} candidates analyzed •{' '}
            {results.timestamp ? new Date(results.timestamp).toLocaleString() : 'Just now'}
          </p>
        </div>
        <button onClick={onDownloadCSV} className="btn-primary flex items-center gap-2">
          <span>📥</span>
          <span>Export Shortlist CSV</span>
        </button>
      </div>

      {/* Filter bar */}
      <div className="glass-card p-4 mb-6 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>
            Confidence:
          </label>
          <select
            value={filterConfidence}
            onChange={(e) => setFilterConfidence(e.target.value)}
            className="input-field py-1.5 px-3 text-xs w-40"
          >
            <option value="all">All</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
            <option value="needs_review">Needs Review</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <label className="text-xs font-semibold" style={{ color: 'var(--color-text-muted)' }}>
            Sort by:
          </label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="input-field py-1.5 px-3 text-xs w-32"
          >
            <option value="rank">Rank</option>
            <option value="score">Score</option>
            <option value="name">Name</option>
          </select>
        </div>

        <div className="flex-1" />

        <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
          Showing {filtered.length} of {results.scorecards.length}
        </span>
      </div>

      {/* Candidate cards */}
      <div className="space-y-3 stagger-children">
        {filtered.map((sc) => (
          <CandidateCard
            key={sc.candidate_id}
            scorecard={sc}
            onClick={() => openDrawer(sc)}
          />
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-12">
          <p className="text-lg" style={{ color: 'var(--color-text-muted)' }}>
            No candidates match the selected filters
          </p>
        </div>
      )}

      {/* Scorecard Drawer */}
      {selectedCandidate && (
        <>
          {/* Overlay */}
          <div
            className={`drawer-overlay ${drawerOpen ? 'animate-fade-in' : 'opacity-0'}`}
            onClick={closeDrawer}
          />

          {/* Drawer panel */}
          <div className={`drawer-panel ${drawerOpen ? 'animate-slide-in-right' : 'animate-slide-out-right'}`}>
            {/* Drawer header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold">{selectedCandidate.candidate_name}</h3>
                <div className="flex items-center gap-2 mt-1">
                  <span className={`rank-badge text-xs ${
                    selectedCandidate.final_rank <= 3 ? `rank-${selectedCandidate.final_rank}` : ''
                  }`}>
                    #{selectedCandidate.final_rank}
                  </span>
                  <VerificationBadge
                    confidence={selectedCandidate.confidence}
                    aiRiskScore={selectedCandidate.ai_risk_score}
                  />
                </div>
              </div>
              <button onClick={closeDrawer}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-white transition-colors"
                      style={{ background: 'var(--color-bg-glass)' }}>
                ✕
              </button>
            </div>

            {/* Overall score */}
            <div className="glass-card p-4 mb-6">
              <div className="flex items-center gap-4">
                <div className={`score-badge text-xl ${
                  selectedCandidate.weighted_total >= 0.75 ? 'high' :
                  selectedCandidate.weighted_total >= 0.5 ? 'mid' : 'low'
                }`}>
                  {(selectedCandidate.weighted_total * 100).toFixed(0)}
                </div>
                <div>
                  <p className="text-sm font-semibold">Overall Score</p>
                  <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                    Confidence: <span className="capitalize">{selectedCandidate.confidence}</span>
                  </p>
                </div>
                <div className="ml-auto text-right">
                  <p className="text-[10px] uppercase tracking-wider"
                     style={{ color: 'var(--color-text-muted)' }}>AI Risk</p>
                  <p className={`text-lg font-bold ${
                    selectedCandidate.ai_risk_score >= 0.7 ? 'text-rose-400' :
                    selectedCandidate.ai_risk_score >= 0.4 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {(selectedCandidate.ai_risk_score * 100).toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Score visualization */}
            <ScoreBreakdown scores={selectedCandidate.scores} />

            {/* Analyst reasoning */}
            <div className="mt-6">
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-2"
                  style={{ color: 'var(--color-text-secondary)' }}>
                Analyst Reasoning
              </h4>
              <div className="rounded-xl p-4 text-sm leading-relaxed"
                   style={{
                     background: 'var(--color-bg-glass)',
                     color: 'var(--color-text-secondary)',
                     border: '1px solid var(--color-border)',
                   }}>
                {selectedCandidate.analyst_reasoning || 'No reasoning provided.'}
              </div>
            </div>

            {/* Challenger flags */}
            {selectedCandidate.challenger_flags?.length > 0 && (
              <div className="mt-6">
                <ChallengerFlags flags={selectedCandidate.challenger_flags} />
              </div>
            )}

            {/* Download button */}
            <div className="mt-8 pt-4" style={{ borderTop: '1px solid var(--color-border)' }}>
              <button className="btn-secondary flex items-center gap-2 w-full justify-center">
                <span>📋</span>
                <span>Download Scorecard JSON</span>
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
