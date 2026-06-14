/**
 * TrueHire API client — all fetch calls to FastAPI backend.
 */

const API_BASE = '/api';

/**
 * Upload raw JD text and get extracted skills.
 * @param {string} rawText - Raw job description text
 * @returns {Promise<{title: string, skills: Array, flagged_count: number}>}
 */
export async function uploadJD(rawText) {
  const res = await fetch(`${API_BASE}/jd/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text: rawText }),
  });
  if (!res.ok) throw new Error(`JD upload failed: ${res.statusText}`);
  return res.json();
}

/**
 * Submit HR priority decisions for extracted skills.
 * @param {string} rawText - Original JD text
 * @param {Array<{name: string, tier: string}>} skills - Skills with assigned tiers
 * @returns {Promise<Object>} WeightedJD
 */
export async function setPriorities(rawText, skills) {
  const res = await fetch(`${API_BASE}/jd/priorities`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_text: rawText, skills }),
  });
  if (!res.ok) throw new Error(`Priority setting failed: ${res.statusText}`);
  return res.json();
}

/**
 * Upload candidate file (CSV or JSON).
 * @param {File} file - The file to upload
 * @returns {Promise<{count: number, candidates: Array}>}
 */
export async function uploadCandidates(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE}/candidates/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) throw new Error(`Candidate upload failed: ${res.statusText}`);
  return res.json();
}

/**
 * Start the analysis pipeline.
 * @returns {Promise<{job_id: string, status: string}>}
 */
export async function runPipeline() {
  const res = await fetch(`${API_BASE}/pipeline/run`, { method: 'POST' });
  if (!res.ok) throw new Error(`Pipeline start failed: ${res.statusText}`);
  return res.json();
}

/**
 * Poll pipeline status.
 * @param {string} jobId
 * @returns {Promise<Object>} PipelineStatusResponse
 */
export async function getPipelineStatus(jobId) {
  const res = await fetch(`${API_BASE}/pipeline/status/${jobId}`);
  if (!res.ok) throw new Error(`Status check failed: ${res.statusText}`);
  return res.json();
}

/**
 * Get ranked results.
 * @param {string} jobId
 * @returns {Promise<Object>} RankedResults
 */
export async function getResults(jobId) {
  const res = await fetch(`${API_BASE}/results/${jobId}`);
  if (!res.ok) throw new Error(`Results fetch failed: ${res.statusText}`);
  return res.json();
}

/**
 * Download ranked CSV.
 * @param {string} jobId
 */
export async function downloadCSV(jobId) {
  const res = await fetch(`${API_BASE}/results/${jobId}/csv`);
  if (!res.ok) throw new Error(`CSV download failed: ${res.statusText}`);
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ranked_candidates_${jobId}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Get individual candidate scorecard.
 * @param {string} candidateId
 * @returns {Promise<Object>} Scorecard
 */
export async function getCandidateScorecard(candidateId) {
  const res = await fetch(`${API_BASE}/candidate/${candidateId}/scorecard`);
  if (!res.ok) throw new Error(`Scorecard fetch failed: ${res.statusText}`);
  return res.json();
}
