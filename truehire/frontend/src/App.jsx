import React, { useState, useCallback, useRef, useEffect } from 'react';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import JDUpload from './components/upload/JDUpload';
import ProfileUpload from './components/upload/ProfileUpload';
import HRGateView from './components/hr_gate/HRGateView';
import PipelineView from './components/pipeline/PipelineView';
import ResultsDashboard from './components/results/ResultsDashboard';
import {
  uploadJD, setPriorities, uploadCandidates,
  runPipeline, getPipelineStatus, getResults, downloadCSV,
} from './api';

/**
 * TrueHire — main application with 4 views.
 */
export default function App() {
  // Navigation
  const [currentView, setCurrentView] = useState('upload');

  // Upload state
  const [jdText, setJdText] = useState('');
  const [skills, setSkills] = useState([]);
  const [jdUploaded, setJdUploaded] = useState(false);
  const [candidatesUploaded, setCandidatesUploaded] = useState(false);
  const [loadingJD, setLoadingJD] = useState(false);
  const [loadingCandidates, setLoadingCandidates] = useState(false);

  // Pipeline state
  const [jobId, setJobId] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [pipelineComplete, setPipelineComplete] = useState(false);
  const [loadingPipeline, setLoadingPipeline] = useState(false);
  const pollingRef = useRef(null);

  // Results state
  const [results, setResults] = useState(null);

  // --- Upload handlers ---
  const handleJDExtract = useCallback(async (text) => {
    setLoadingJD(true);
    try {
      const response = await uploadJD(text);
      setJdText(text);
      setSkills(response.skills.map(s => ({ ...s })));
      setJdUploaded(true);
    } catch (err) {
      console.error('JD upload failed:', err);
      alert('Failed to extract skills. Please try again.');
    } finally {
      setLoadingJD(false);
    }
  }, []);

  const handleCandidatesUpload = useCallback(async (file) => {
    setLoadingCandidates(true);
    try {
      const response = await uploadCandidates(file);
      setCandidatesUploaded(true);
      return response;
    } catch (err) {
      console.error('Candidate upload failed:', err);
      alert('Failed to upload candidates. Please check file format.');
    } finally {
      setLoadingCandidates(false);
    }
  }, []);

  // --- HR Gate handlers ---
  const handleTierChange = useCallback((skillName, tier) => {
    setSkills(prev => prev.map(s =>
      s.name === skillName ? { ...s, tier } : s
    ));
  }, []);

  const handleConfirmPriorities = useCallback(async () => {
    setLoadingPipeline(true);
    try {
      // Set priorities
      const skillPriorities = skills.map(s => ({ name: s.name, tier: s.tier }));
      await setPriorities(jdText, skillPriorities);

      // Start pipeline
      const { job_id } = await runPipeline();
      setJobId(job_id);
      setCurrentView('pipeline');

      // Start polling
      startPolling(job_id);
    } catch (err) {
      console.error('Pipeline start failed:', err);
      alert('Failed to start pipeline. Please try again.');
    } finally {
      setLoadingPipeline(false);
    }
  }, [skills, jdText]);

  // --- Pipeline polling ---
  const startPolling = useCallback((id) => {
    if (pollingRef.current) clearInterval(pollingRef.current);

    pollingRef.current = setInterval(async () => {
      try {
        const status = await getPipelineStatus(id);
        setPipelineStatus(status);

        if (status.status === 'complete' || status.status === 'error') {
          clearInterval(pollingRef.current);
          pollingRef.current = null;

          if (status.status === 'complete') {
            setPipelineComplete(true);
            // Fetch results
            const res = await getResults(id);
            setResults(res);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }, 2000);
  }, []);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const handlePipelineComplete = useCallback(() => {
    setCurrentView('results');
  }, []);

  // --- Results handlers ---
  const handleDownloadCSV = useCallback(() => {
    if (jobId) downloadCSV(jobId);
  }, [jobId]);

  // --- Navigation ---
  const handleNavigate = useCallback((view) => {
    setCurrentView(view);
  }, []);

  // --- Render views ---
  const renderView = () => {
    switch (currentView) {
      case 'upload':
        return (
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold mb-1">Upload</h2>
              <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                Provide the job description and candidate profiles to begin analysis
              </p>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <JDUpload onExtracted={handleJDExtract} loading={loadingJD} />
              <ProfileUpload onUploaded={handleCandidatesUpload} loading={loadingCandidates} />
            </div>

            {/* Ready indicator */}
            {jdUploaded && candidatesUploaded && (
              <div className="mt-6 text-center animate-fade-in">
                <div className="glass-card inline-flex items-center gap-3 px-6 py-3">
                  <span className="text-emerald-400">✓</span>
                  <span className="text-sm font-semibold">
                    Both uploaded! Proceed to{' '}
                    <button
                      onClick={() => setCurrentView('hr_gate')}
                      className="text-purple-400 hover:text-purple-300 underline underline-offset-2"
                    >
                      Skill Prioritization →
                    </button>
                  </span>
                </div>
              </div>
            )}
          </div>
        );

      case 'hr_gate':
        return (
          <HRGateView
            skills={skills}
            onTierChange={handleTierChange}
            onConfirm={handleConfirmPriorities}
            loading={loadingPipeline}
          />
        );

      case 'pipeline':
        return (
          <PipelineView
            status={pipelineStatus}
            onComplete={handlePipelineComplete}
          />
        );

      case 'results':
        return (
          <ResultsDashboard
            results={results}
            onDownloadCSV={handleDownloadCSV}
          />
        );

      default:
        return null;
    }
  };

  return (
    <div className="app-layout">
      <Navbar currentView={currentView} />
      <Sidebar
        currentView={currentView}
        onNavigate={handleNavigate}
        jdUploaded={jdUploaded}
        candidatesUploaded={candidatesUploaded}
        pipelineComplete={pipelineComplete}
      />
      <main className="app-content">
        {renderView()}
      </main>
    </div>
  );
}
