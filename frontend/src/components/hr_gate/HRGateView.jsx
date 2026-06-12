import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { runPipeline } from '../../api';

export default function HRGateView({ jdData, setJdData, candidatesData, setJobId }) {
  const navigate = useNavigate();
  const [skills, setSkills] = useState(jdData?.skills || []);

  const handleTierChange = (index, tier) => {
    const newSkills = [...skills];
    newSkills[index].tier = tier;
    setSkills(newSkills);
  };

  const handleConfirm = async () => {
    const finalJd = { ...jdData, skills };
    setJdData(finalJd);
    
    const res = await runPipeline(finalJd, candidatesData);
    setJobId(res.job_id);
    navigate('/pipeline');
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-2xl font-bold mb-6">HR Priority Gate</h2>
      <p className="mb-4 text-gray-600">Review the extracted skills and set their importance.</p>
      
      <div className="space-y-4">
        {skills.map((skill, i) => (
          <div key={i} className="bg-white p-4 rounded shadow border-l-4 border-indigo-500 flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-lg">{skill.name}</h3>
              {skill.flagged && <span className="text-sm text-red-500 font-bold">⚠ Flagged: Potentially inflated</span>}
            </div>
            <div className="flex gap-2">
              {['blocker', 'important', 'nice_to_have'].map(t => (
                <button 
                  key={t}
                  onClick={() => handleTierChange(i, t)}
                  className={`px-3 py-1 text-sm rounded border ${skill.tier === t ? 'bg-indigo-100 border-indigo-600 text-indigo-700' : 'bg-gray-50 text-gray-600'}`}
                >
                  {t.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-8 flex justify-end">
        <button onClick={handleConfirm} className="bg-indigo-600 text-white px-6 py-2 rounded font-medium shadow">
          Confirm & Run Pipeline
        </button>
      </div>
    </div>
  );
}
