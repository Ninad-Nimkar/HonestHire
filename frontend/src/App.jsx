import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import UploadView from './components/upload/UploadView';
import HRGateView from './components/hr_gate/HRGateView';
import PipelineView from './components/pipeline/PipelineView';
import ResultsDashboard from './components/results/ResultsDashboard';

function AppLayout() {
  const [jdData, setJdData] = useState(null);
  const [candidatesData, setCandidatesData] = useState([]);
  const [jobId, setJobId] = useState(null);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white shadow p-4 font-bold text-xl text-indigo-600">TrueHire</header>
      <main className="flex-1 p-8">
        <Routes>
          <Route path="/" element={<UploadView setJdData={setJdData} setCandidatesData={setCandidatesData} />} />
          <Route path="/gate" element={<HRGateView jdData={jdData} setJdData={setJdData} candidatesData={candidatesData} setJobId={setJobId} />} />
          <Route path="/pipeline" element={<PipelineView jobId={jobId} />} />
          <Route path="/results" element={<ResultsDashboard jobId={jobId} />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}
