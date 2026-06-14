# TrueHire — AI-Powered Candidate Ranking System

> Ranks job candidates the way a great recruiter would — not by keyword matching but by genuinely understanding fit.

TrueHire reads a job description, analyzes candidate profiles holistically, verifies their online presence for authenticity, and delivers a trusted shortlist with explainable scores. It uses a dual-LLM debate mechanism where one AI scores candidates and another challenges those scores.

## ✨ Features

- **LLM-Powered JD Parsing** — Extracts skills from job descriptions and flags inflated requirements
- **HR Priority Gate** — Interactive skill tiering where HR controls what matters most
- **12-Node Analysis Pipeline** — LangGraph-orchestrated pipeline with real-time progress
- **Dual-LLM Debate** — GPT-4o "analyst" scores, GPT-4o "challenger" finds weaknesses
- **GitHub & Social Verification** — Checks online presence for authenticity signals
- **AI Content Detection** — Heuristic detection of AI-generated portfolios (no external APIs)
- **Skill Transfer Inference** — Maps adjacent skills with confidence scoring
- **Interactive Results Dashboard** — Ranked candidates with radar charts, scorecard drawers, CSV export

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **OpenAI API key** (required for LLM-powered analysis)

## 🔧 Setup

### 1. Clone & configure environment

```bash
cd truehire
```

Create a `.env` file in the **project root** (parent of `truehire/`):

```env
OPENAI_API_KEY=sk-your-openai-key-here
GITHUB_TOKEN=ghp-your-github-token       # Optional: higher API rate limits
PROXYCURL_KEY=your-proxycurl-key          # Optional: LinkedIn enrichment
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

## 🚀 Running

### Start the backend (API server)

```bash
cd truehire/backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`. 
API docs at `http://localhost:8000/docs`.

### Start the frontend (dev server)

```bash
cd truehire/frontend
npm run dev
```

The dashboard will open at `http://localhost:5173`.

## 🎯 Example Walkthrough

### Step 1: Upload
1. Open `http://localhost:5173`
2. **Left panel**: Paste the sample JD from `backend/data/sample/sample_jd.txt`
3. Click **"Extract Skills"** — the AI identifies 13 skills with suggested tiers
4. **Right panel**: Upload `backend/data/sample/candidates.json`
5. Both panels show ✓ — proceed to prioritization

### Step 2: Prioritize Skills
- Rate each skill as **BLOCKER** / **IMPORTANT** / **NICE TO HAVE**
- Note the ⚠️ flags on inflated requirements (e.g., "10+ years of Kubernetes")
- Click **"Confirm & Run Pipeline"**

### Step 3: Watch the Pipeline
- 12 pipeline nodes execute in sequence with real-time progress
- Each node shows status, elapsed time, and completion

### Step 4: View Results
- Candidates ranked by weighted total score
- Click any candidate to open the full scorecard drawer with:
  - Radar chart of 5 scoring axes
  - Analyst reasoning
  - Challenger flags
  - AI risk score
- Export shortlist as CSV

### Expected ranking with sample data:
1. 🥇 **Priya Sharma** — Strong genuine match, verified GitHub, high scores
2. 🥈 **Sarah Chen** — Adjacent fit with strong transferable skills
3. 🥉 **Marcus Johnson** — Underrated non-traditional candidate, real OSS contributions
4. ⚠️ **Alex Rivera** — AI-generated portfolio flags, needs review
5. 🚩 **Kevin Zhang** — Keyword-stuffed, broken links, inflated claims

## 📁 Project Structure

```
truehire/
├── backend/
│   ├── main.py                    # FastAPI app, all API routes
│   ├── config.py                  # Environment config via pydantic-settings
│   ├── requirements.txt
│   ├── models/                    # Pydantic V2 data models
│   │   ├── jd.py                  # Job description & skill models
│   │   ├── candidate.py           # Candidate profile & verification
│   │   └── scorecard.py           # Scoring & pipeline status
│   ├── pipeline/
│   │   ├── graph.py               # LangGraph pipeline definition
│   │   ├── state.py               # Shared pipeline state
│   │   └── nodes/                 # 12 pipeline nodes
│   ├── data/
│   │   ├── skill_graph.json       # Skill adjacency map (35+ technologies)
│   │   └── sample/                # Sample JD + candidate data
│   └── output/                    # Pipeline output (CSV + scorecards)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Main app with 4-view routing
│   │   ├── api.js                 # API client
│   │   ├── components/
│   │   │   ├── layout/            # Navbar, Sidebar
│   │   │   ├── upload/            # JD & candidate upload
│   │   │   ├── hr_gate/           # Skill tiering UI
│   │   │   ├── pipeline/          # Live progress view
│   │   │   └── results/           # Ranked dashboard + scorecard drawer
│   │   └── styles/
│   │       └── index.css          # Design system + Tailwind
│   └── vite.config.js             # Vite + API proxy
│
└── README.md
```

## 🔌 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/jd/upload` | Upload JD text → extract skills |
| POST | `/api/jd/priorities` | Set skill tiers → WeightedJD |
| POST | `/api/candidates/upload` | Upload candidate CSV/JSON |
| POST | `/api/pipeline/run` | Start pipeline → job_id |
| GET | `/api/pipeline/status/{id}` | Poll pipeline progress |
| GET | `/api/results/{job_id}` | Full ranked results |
| GET | `/api/results/{job_id}/csv` | Download CSV |
| GET | `/api/candidate/{id}/scorecard` | Individual scorecard |

## 🧠 Pipeline Nodes

| # | Node | Purpose |
|---|------|---------|
| 1 | JD Parser | GPT-4o extracts skills from JD |
| 2 | HR Gate | Applies tier weights, flags inflation |
| 3 | Profile Parser | Structures raw CVs with LLM |
| 4 | Link Verifier | HTTP checks + identity matching |
| 5 | GitHub Analyzer | Commit patterns, bulk push detection |
| 6 | Social Analyzer | LinkedIn/Twitter cross-referencing |
| 7 | AI Detector | Heuristic AI content detection |
| 8 | Skill Transfer | Adjacency-based skill inference |
| 9 | LLM Analyst | GPT-4o scores on 5 axes |
| 10 | LLM Challenger | GPT-4o challenges analyst scores |
| 11 | Synthesizer | Merges outputs, applies penalties |
| 12 | Ranker | Filters blockers, assigns ranks, writes CSV |

## 📝 License

MIT
