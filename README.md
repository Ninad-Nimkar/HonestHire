# TrueHire

An AI-powered candidate ranking system that evaluates candidates like a great recruiter. It features a React/Vite frontend dashboard and a FastAPI/LangGraph backend that orchestrated complex candidate verification and LLM analysis pipelines.

## Project Structure
- `backend/`: FastAPI server, LangGraph workflow, data models.
- `frontend/`: React + Vite SPA, Tailwind CSS, Recharts for visualizations.

## Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- OpenAI API Key

## Setup Instructions

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
GITHUB_TOKEN=your_github_token_here (optional, for higher rate limits)
```

Run the backend server:
```bash
uvicorn main:app --reload --port 8000
```
API runs on `http://localhost:8000`.

### 2. Frontend
```bash
cd frontend
npm install
```

Run the frontend development server:
```bash
npm run dev
```
Frontend runs on `http://localhost:5173`.

## Example Run Walkthrough

1. Open the UI at `http://localhost:5173`.
2. **Upload JD**: Copy the text from `backend/data/sample/sample_jd.txt` into the Job Description text area.
3. **Upload Candidates**: Upload the `backend/data/sample/candidates.json` file via the drag-drop zone.
4. Click **Extract Skills**.
5. **HR Priority Gate**: Review the extracted skills. Adjust the tier (Blocker, Important, Nice to Have) for each skill. You will see flags for potentially inflated skills.
6. Click **Confirm & Run Pipeline**.
7. **Pipeline Progress**: Watch the live LangGraph execution progress as it orchestrates extracting profiles, verifying links, analyzing GitHub, running AI detection, scoring with an LLM Analyst, and auditing with an LLM Challenger.
8. **Results Dashboard**: Review the final rankings! Expand a candidate's scorecard to view the 5-axis radar chart, AI risk scores, and specific LLM Challenger flags.
