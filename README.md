# TrueHire

An AI-powered candidate ranking system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables in `.env` (or configure your shell):
```
ANTHROPIC_API_KEY=your_key
GITHUB_TOKEN=your_token
```

3. Run:
```bash
python main.py --jd data/sample/jd.txt --cvs data/sample/cvs/
```

## Structure
- `models/`: Pydantic models for structured outputs
- `pipeline/`: LangGraph orchestration and nodes
- `data/`: Skill graph and sample JDs/CVs
- `output/`: Results will be stored here
