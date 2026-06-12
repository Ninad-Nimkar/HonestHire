import React, { useEffect, useState } from 'react';
import { getResults } from '../../api';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

export default function ResultsDashboard({ jobId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!jobId) return;
    getResults(jobId).then(setData).catch(console.error);
  }, [jobId]);

  if (!data) return <div className="text-center mt-20 text-xl">Loading results...</div>;

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-800">Results Dashboard</h2>
          <p className="text-gray-500">{data.candidates.length} candidates analyzed</p>
        </div>
        <button className="bg-gray-800 text-white px-4 py-2 rounded shadow">Export Shortlist CSV</button>
      </div>

      <div className="grid gap-6">
        {data.candidates.map((cand, i) => (
          <CandidateCard key={i} candidate={cand} />
        ))}
      </div>
    </div>
  );
}

function CandidateCard({ candidate: c }) {
  const [expanded, setExpanded] = useState(false);
  
  const radarData = [
    { subject: 'Skills', A: c.scores.skills_fit * 100 },
    { subject: 'Experience', A: c.scores.experience_relevance * 100 },
    { subject: 'Behavior', A: c.scores.behavioral_signals * 100 },
    { subject: 'Trajectory', A: c.scores.trajectory * 100 },
    { subject: 'Social', A: c.scores.social_credibility * 100 },
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
      <div className="flex justify-between items-center cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center font-bold text-indigo-700 text-xl">
            #{c.final_rank}
          </div>
          <div>
            <h3 className="text-xl font-bold">{c.name}</h3>
            <p className="text-sm text-gray-500">Match: {(c.weighted_total * 100).toFixed(1)}%</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {c.confidence === 'high' ? (
            <span className="text-green-600 bg-green-50 px-3 py-1 rounded-full text-sm font-medium">✓ Verified</span>
          ) : (
            <span className="text-yellow-600 bg-yellow-50 px-3 py-1 rounded-full text-sm font-medium">⚠ Needs Review</span>
          )}
        </div>
      </div>
      
      {expanded && (
        <div className="mt-6 border-t pt-6 grid grid-cols-2 gap-8">
          <div>
            <h4 className="font-semibold mb-4 text-gray-700">Score Breakdown</h4>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} />
                  <Radar name="Candidate" dataKey="A" stroke="#4f46e5" fill="#4f46e5" fillOpacity={0.6} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div>
            <h4 className="font-semibold mb-2 text-gray-700">Analyst Notes</h4>
            <p className="text-gray-600 text-sm mb-4">{c.analyst_reasoning || 'Strong candidate overall with verifiable history.'}</p>
            
            {c.challenger_flags?.length > 0 && (
              <>
                <h4 className="font-semibold mb-2 text-red-700">Challenger Flags</h4>
                <ul className="list-disc pl-5 text-sm text-red-600 space-y-1">
                  {c.challenger_flags.map((flag, idx) => <li key={idx}>{flag}</li>)}
                </ul>
              </>
            )}
            
            <div className="mt-4">
              <p className="text-sm text-gray-500">AI Risk Score: {(c.ai_risk_score * 100).toFixed(0)}%</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
