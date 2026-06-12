import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadJD, uploadCandidates } from '../../api';

export default function UploadView({ setJdData, setCandidatesData }) {
  const [jdText, setJdText] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleStart = async () => {
    setLoading(true);
    try {
      const jdRes = await uploadJD(jdText);
      let candRes = { raw_cvs: [] };
      if (file) {
        candRes = await uploadCandidates(file);
      }
      setJdData({ raw_text: jdText, skills: jdRes.skills });
      setCandidatesData(candRes.raw_cvs.map(cv => ({ raw_cv: cv })));
      navigate('/gate');
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="grid grid-cols-2 gap-8 h-full">
      <div className="bg-white p-6 rounded shadow flex flex-col">
        <h2 className="text-xl font-semibold mb-4">Job Description</h2>
        <textarea 
          className="flex-1 border p-2 w-full rounded" 
          placeholder="Paste Job Description here..."
          value={jdText}
          onChange={(e) => setJdText(e.target.value)}
        />
      </div>
      <div className="bg-white p-6 rounded shadow flex flex-col items-center justify-center border-dashed border-2">
        <h2 className="text-xl font-semibold mb-4">Upload Candidates</h2>
        <input type="file" onChange={(e) => setFile(e.target.files[0])} />
        {file && <p className="mt-4 text-green-600 font-medium">Selected: {file.name}</p>}
      </div>
      <div className="col-span-2 flex justify-end mt-4">
        <button 
          onClick={handleStart} 
          disabled={!jdText || loading}
          className="bg-indigo-600 text-white px-6 py-2 rounded shadow disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Extract Skills'}
        </button>
      </div>
    </div>
  );
}
