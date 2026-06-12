import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPipelineStatus } from '../../api';

export default function PipelineView({ jobId }) {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!jobId) return;
    
    const interval = setInterval(async () => {
      try {
        const res = await getPipelineStatus(jobId);
        setStatus(res);
        if (res.status === 'complete') {
          clearInterval(interval);
          navigate('/results');
        }
      } catch (err) {
        console.error(err);
      }
    }, 2000);
    
    return () => clearInterval(interval);
  }, [jobId, navigate]);

  return (
    <div className="max-w-2xl mx-auto text-center mt-20">
      <h2 className="text-3xl font-bold mb-8">Running Analysis...</h2>
      <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
        <div 
          className="bg-indigo-600 h-4 rounded-full transition-all duration-500" 
          style={{ width: `${status?.progress || 0}%` }}
        ></div>
      </div>
      <p className="text-xl text-gray-700 mt-4 capitalize">
        Current step: {status?.node?.replace('_', ' ') || 'Initializing'}
      </p>
    </div>
  );
}
