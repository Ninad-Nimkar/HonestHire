import React from 'react';
import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';

/**
 * Score breakdown — radar chart + bar chart for 5 scoring axes.
 */
export default function ScoreBreakdown({ scores, compact = false }) {
  if (!scores) return null;

  const axisLabels = {
    skills_fit: 'Skills Fit',
    experience_relevance: 'Experience',
    behavioral_signals: 'Behavioral',
    trajectory: 'Trajectory',
    social_credibility: 'Social Cred.',
  };

  const radarData = Object.entries(axisLabels).map(([key, label]) => ({
    axis: label,
    value: (scores[key] || 0) * 100,
    fullMark: 100,
  }));

  const barData = Object.entries(axisLabels).map(([key, label]) => ({
    name: label,
    score: scores[key] || 0,
  }));

  const getBarColor = (score) => {
    if (score >= 0.75) return '#10b981';
    if (score >= 0.5) return '#f59e0b';
    return '#f43f5e';
  };

  if (compact) {
    // Mini bars for candidate card
    return (
      <div className="flex gap-1 items-end h-8">
        {barData.map((d, i) => (
          <div key={i} className="flex flex-col items-center gap-0.5 flex-1">
            <div className="w-full rounded-sm"
                 style={{
                   height: `${Math.max(d.score * 28, 2)}px`,
                   background: getBarColor(d.score),
                   opacity: 0.7,
                 }} />
            <span className="text-[8px]" style={{ color: 'var(--color-text-muted)' }}>
              {d.name.slice(0, 3)}
            </span>
          </div>
        ))}
      </div>
    );
  }

  // Full view with radar + bar
  return (
    <div className="space-y-6">
      {/* Radar Chart */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider mb-3"
            style={{ color: 'var(--color-text-secondary)' }}>
          Competency Radar
        </h4>
        <div className="rounded-xl p-4" style={{ background: 'var(--color-bg-glass)' }}>
          <ResponsiveContainer width="100%" height={260}>
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="72%">
              <PolarGrid stroke="rgba(255,255,255,0.06)" />
              <PolarAngleAxis
                dataKey="axis"
                tick={{ fill: '#9ca3af', fontSize: 11 }}
              />
              <PolarRadiusAxis
                angle={90}
                domain={[0, 100]}
                tick={{ fill: '#6b7280', fontSize: 9 }}
                axisLine={false}
              />
              <Radar
                name="Score"
                dataKey="value"
                stroke="#7c3aed"
                fill="#7c3aed"
                fillOpacity={0.2}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Bar Chart */}
      <div>
        <h4 className="text-xs font-semibold uppercase tracking-wider mb-3"
            style={{ color: 'var(--color-text-secondary)' }}>
          Score Breakdown
        </h4>
        <div className="rounded-xl p-4" style={{ background: 'var(--color-bg-glass)' }}>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={barData} layout="vertical" margin={{ left: 0 }}>
              <XAxis type="number" domain={[0, 1]} tick={{ fill: '#6b7280', fontSize: 10 }} />
              <YAxis
                type="category"
                dataKey="name"
                width={80}
                tick={{ fill: '#9ca3af', fontSize: 11 }}
              />
              <Tooltip
                contentStyle={{
                  background: '#1f2937',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#f9fafb',
                  fontSize: '12px',
                }}
                formatter={(value) => [`${(value * 100).toFixed(0)}%`, 'Score']}
              />
              <Bar dataKey="score" radius={[0, 4, 4, 0]} barSize={16}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={getBarColor(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
