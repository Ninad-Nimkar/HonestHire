import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const uploadJD = async (text) => {
  const res = await axios.post(`${API_BASE}/jd/upload`, { text });
  return res.data;
};

export const uploadCandidates = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await axios.post(`${API_BASE}/candidates/upload`, formData);
  return res.data;
};

export const runPipeline = async (jd, candidates) => {
  const res = await axios.post(`${API_BASE}/pipeline/run`, { jd, candidates });
  return res.data;
};

export const getPipelineStatus = async (jobId) => {
  const res = await axios.get(`${API_BASE}/pipeline/status/${jobId}`);
  return res.data;
};

export const getResults = async (jobId) => {
  const res = await axios.get(`${API_BASE}/results/${jobId}`);
  return res.data;
};
